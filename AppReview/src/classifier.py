"""
评论分类与关键词统计模块
使用 jieba 进行中文分词，SnowNLP 进行情感分析
"""
import json
import os
from typing import List, Dict, Tuple
from collections import Counter

import jieba
import jieba.analyse
from snownlp import SnowNLP

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    RATING_CATEGORIES, KEYWORD_CATEGORIES, STOPWORDS,
    SENTIMENT_POSITIVE_THRESHOLD, SENTIMENT_NEGATIVE_THRESHOLD,
    DATA_DIR, OUTPUT_ANALYSIS_JSON
)


class ReviewClassifier:
    """评论分类器"""
    
    def __init__(self):
        # 添加自定义词汇到 jieba
        custom_words = [
            "小米", "红米", "互联服务", "米家", "小爱", "小爱同学",
            "手环", "手表", "耳机", "音箱", "智能家居", "门锁", "摄像头",
            "连不上", "断连", "闪退", "卡顿", "耗电", "好用", "难用",
            "蓝牙", "WiFi", "配对", "同步", "推送", "通知",
        ]
        for word in custom_words:
            jieba.add_word(word)
        
        # 设置停用词
        self.stopwords = set(STOPWORDS)
    
    def segment_text(self, text: str) -> List[str]:
        """
        使用 jieba 对文本进行分词
        
        Args:
            text: 待分词文本
        
        Returns:
            分词结果列表（已过滤停用词）
        """
        words = jieba.lcut(text)
        # 过滤停用词和单字
        filtered = [w.strip() for w in words if w.strip() and len(w.strip()) >= 2 and w not in self.stopwords]
        return filtered
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        提取文本关键词（使用 TF-IDF）
        
        Args:
            text: 文本
            top_k: 返回前 k 个关键词
        
        Returns:
            关键词及权重列表
        """
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        return keywords
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        分析文本情感
        
        Args:
            text: 文本
        
        Returns:
            (情感分数, 情感标签)
        """
        if not text.strip():
            return 0.5, "中性"
        
        try:
            s = SnowNLP(text)
            score = s.sentiments
            
            if score >= SENTIMENT_POSITIVE_THRESHOLD:
                sentiment = "正面"
            elif score <= SENTIMENT_NEGATIVE_THRESHOLD:
                sentiment = "负面"
            else:
                sentiment = "中性"
            
            return score, sentiment
        except:
            return 0.5, "中性"
    
    def classify_by_rating(self, reviews: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按评分分类评论
        
        Args:
            reviews: 评论列表
        
        Returns:
            分类后的评论字典
        """
        result = {category: [] for category in RATING_CATEGORIES.keys()}
        
        for review in reviews:
            rating = review.get("rating", 0)
            for category, ratings in RATING_CATEGORIES.items():
                if rating in ratings:
                    result[category].append(review)
                    break
        
        return result
    
    def classify_by_keywords(self, reviews: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按关键词分类评论
        
        Args:
            reviews: 评论列表
        
        Returns:
            分类后的评论字典
        """
        result = {category: [] for category in KEYWORD_CATEGORIES.keys()}
        result["其他"] = []
        
        for review in reviews:
            full_text = review.get("full_text", "")
            classified = False
            
            for category, keywords in KEYWORD_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in full_text:
                        result[category].append(review)
                        classified = True
                        break
                if classified:
                    break
            
            if not classified:
                result["其他"].append(review)
        
        return result
    
    def classify_by_sentiment(self, reviews: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按情感分类评论
        
        Args:
            reviews: 评论列表
        
        Returns:
            分类后的评论字典
        """
        result = {"正面": [], "中性": [], "负面": []}
        
        for review in reviews:
            full_text = review.get("full_text", "")
            _, sentiment = self.analyze_sentiment(full_text)
            result[sentiment].append(review)
        
        return result
    
    def get_word_frequency(self, reviews: List[Dict], top_n: int = 30) -> List[Tuple[str, int]]:
        """
        统计词频
        
        Args:
            reviews: 评论列表
            top_n: 返回前 n 个高频词
        
        Returns:
            高频词列表 [(词, 频次), ...]
        """
        all_words = []
        
        for review in reviews:
            full_text = review.get("full_text", "")
            words = self.segment_text(full_text)
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        return word_counts.most_common(top_n)
    
    def get_keywords_tfidf(self, reviews: List[Dict], top_n: int = 20) -> List[Tuple[str, float]]:
        """
        使用 TF-IDF 提取关键词
        
        Args:
            reviews: 评论列表
            top_n: 返回前 n 个关键词
        
        Returns:
            关键词列表 [(词, 权重), ...]
        """
        all_text = " ".join([review.get("full_text", "") for review in reviews])
        keywords = jieba.analyse.extract_tags(all_text, topK=top_n, withWeight=True)
        return keywords
    
    def analyze_all(self, reviews: List[Dict]) -> Dict:
        """
        对评论进行全面分析
        
        Args:
            reviews: 评论列表
        
        Returns:
            分析结果字典
        """
        # 按评分分类
        by_rating = self.classify_by_rating(reviews)
        
        # 按关键词分类
        by_keywords = self.classify_by_keywords(reviews)
        
        # 按情感分类
        by_sentiment = self.classify_by_sentiment(reviews)
        
        # 词频统计
        word_freq = self.get_word_frequency(reviews, top_n=30)
        
        # TF-IDF 关键词
        keywords_tfidf = self.get_keywords_tfidf(reviews, top_n=20)
        
        # 计算评分分布
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = review.get("rating", 0)
            if rating in rating_dist:
                rating_dist[rating] += 1
        
        total = len(reviews) if reviews else 1
        avg_rating = sum(r * c for r, c in rating_dist.items()) / total if total > 0 else 0
        
        return {
            "summary": {
                "total_reviews": len(reviews),
                "average_rating": round(avg_rating, 2),
                "rating_distribution": rating_dist
            },
            "by_rating": {
                cat: {
                    "count": len(items),
                    "percentage": round(len(items) / total * 100, 1) if total > 0 else 0,
                    "samples": [r.get("full_text", "")[:100] for r in items[:3]]
                }
                for cat, items in by_rating.items()
            },
            "by_keywords": {
                cat: {
                    "count": len(items),
                    "percentage": round(len(items) / total * 100, 1) if total > 0 else 0,
                    "samples": [r.get("full_text", "")[:100] for r in items[:3]]
                }
                for cat, items in by_keywords.items() if items
            },
            "by_sentiment": {
                cat: {
                    "count": len(items),
                    "percentage": round(len(items) / total * 100, 1) if total > 0 else 0,
                    "samples": [r.get("full_text", "")[:100] for r in items[:3]]
                }
                for cat, items in by_sentiment.items()
            },
            "word_frequency": word_freq,
            "keywords_tfidf": keywords_tfidf
        }
    
    def save_analysis(self, analysis: Dict, filename: str = None) -> str:
        """
        保存分析结果到 JSON 文件
        
        Args:
            analysis: 分析结果
            filename: 文件名（可选）
        
        Returns:
            保存的文件路径
        """
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename or OUTPUT_ANALYSIS_JSON)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        return filepath


if __name__ == "__main__":
    # 测试分类器
    classifier = ReviewClassifier()
    
    # 测试分词
    test_text = "小米互联服务连接不上蓝牙设备，经常断连，太难用了"
    words = classifier.segment_text(test_text)
    print(f"分词结果: {words}")
    
    # 测试情感分析
    score, sentiment = classifier.analyze_sentiment(test_text)
    print(f"情感分析: {sentiment} (分数: {score:.2f})")
