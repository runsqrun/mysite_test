"""
评论分类器 - 对豆瓣电影评论进行分类和统计
支持按评分、情感、热度等多种方式分类
"""
import json
import os
from typing import List, Dict, Tuple
from collections import Counter
import pandas as pd

try:
    from snownlp import SnowNLP
except ImportError:
    print("请安装snownlp: pip install snownlp")
    SnowNLP = None

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    RATING_TEXT_MAP, RATING_CATEGORIES,
    SENTIMENT_POSITIVE_THRESHOLD, SENTIMENT_NEGATIVE_THRESHOLD,
    DATA_DIR, OUTPUT_STATS_JSON, OUTPUT_CLASSIFIED_JSON
)


class CommentClassifier:
    """评论分类器"""
    
    def __init__(self, comments: List[Dict] = None, reviews: List[Dict] = None):
        """
        初始化分类器
        
        Args:
            comments: 短评列表
            reviews: 长评列表
        """
        self.comments = comments or []
        self.reviews = reviews or []
        self.classified_data = {}
        self.statistics = {}
    
    def load_from_csv(self, comments_file: str = None, reviews_file: str = None):
        """
        从CSV文件加载数据
        
        Args:
            comments_file: 短评CSV文件路径
            reviews_file: 长评CSV文件路径
        """
        if comments_file and os.path.exists(comments_file):
            df = pd.read_csv(comments_file)
            self.comments = df.to_dict('records')
            print(f"已加载 {len(self.comments)} 条短评")
        
        if reviews_file and os.path.exists(reviews_file):
            df = pd.read_csv(reviews_file)
            self.reviews = df.to_dict('records')
            print(f"已加载 {len(self.reviews)} 条长评")
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        分析文本情感
        
        Args:
            text: 待分析的文本
            
        Returns:
            (情感分数0-1, 情感类别)
        """
        if not text or not SnowNLP:
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
            
        except Exception as e:
            print(f"情感分析出错: {e}")
            return 0.5, "中性"
    
    def classify_by_rating(self) -> Dict[str, List[Dict]]:
        """
        按评分分类
        
        Returns:
            按评分分类的评论字典
        """
        result = {category: [] for category in RATING_CATEGORIES.keys()}
        
        for comment in self.comments:
            rating = comment.get('rating', 0)
            for category, ratings in RATING_CATEGORIES.items():
                if rating in ratings:
                    result[category].append(comment)
                    break
        
        self.classified_data['by_rating'] = result
        return result
    
    def classify_by_sentiment(self) -> Dict[str, List[Dict]]:
        """
        按情感分类
        
        Returns:
            按情感分类的评论字典
        """
        result = {
            "正面": [],
            "中性": [],
            "负面": []
        }
        
        print("正在进行情感分析...")
        for i, comment in enumerate(self.comments):
            content = comment.get('content', '')
            score, sentiment = self.analyze_sentiment(content)
            
            # 添加情感信息到评论
            comment['sentiment_score'] = score
            comment['sentiment'] = sentiment
            
            result[sentiment].append(comment)
            
            # 进度显示
            if (i + 1) % 100 == 0:
                print(f"已分析 {i + 1}/{len(self.comments)} 条评论")
        
        self.classified_data['by_sentiment'] = result
        return result
    
    def classify_by_popularity(self, top_n: int = 100) -> Dict[str, List[Dict]]:
        """
        按热度（有用数）分类
        
        Args:
            top_n: 热门评论数量
            
        Returns:
            热度分类结果
        """
        sorted_comments = sorted(
            self.comments,
            key=lambda x: x.get('votes', 0),
            reverse=True
        )
        
        result = {
            "热门评论": sorted_comments[:top_n],
            "普通评论": sorted_comments[top_n:]
        }
        
        self.classified_data['by_popularity'] = result
        return result
    
    def classify_all(self) -> Dict:
        """
        执行所有分类
        
        Returns:
            所有分类结果
        """
        print("\n" + "="*50)
        print("开始分类评论...")
        print("="*50)
        
        print("\n1. 按评分分类...")
        self.classify_by_rating()
        
        print("\n2. 按情感分类...")
        self.classify_by_sentiment()
        
        print("\n3. 按热度分类...")
        self.classify_by_popularity()
        
        return self.classified_data
    
    def generate_statistics(self) -> Dict:
        """
        生成统计数据
        
        Returns:
            统计结果字典
        """
        stats = {
            "总评论数": {
                "短评": len(self.comments),
                "长评": len(self.reviews),
                "合计": len(self.comments) + len(self.reviews)
            },
            "评分分布": {},
            "情感分布": {},
            "热度统计": {},
            "关键词统计": {}
        }
        
        # 评分分布统计
        if 'by_rating' in self.classified_data:
            for category, comments in self.classified_data['by_rating'].items():
                count = len(comments)
                percentage = count / len(self.comments) * 100 if self.comments else 0
                stats["评分分布"][category] = {
                    "数量": count,
                    "占比": f"{percentage:.1f}%"
                }
        
        # 详细评分统计（1-5星）
        rating_counter = Counter([c.get('rating', 0) for c in self.comments])
        stats["详细评分"] = {}
        for rating in range(5, 0, -1):
            count = rating_counter.get(rating, 0)
            percentage = count / len(self.comments) * 100 if self.comments else 0
            stats["详细评分"][f"{rating}星 ({RATING_TEXT_MAP.get(rating, '')})"] = {
                "数量": count,
                "占比": f"{percentage:.1f}%"
            }
        
        # 情感分布统计
        if 'by_sentiment' in self.classified_data:
            for sentiment, comments in self.classified_data['by_sentiment'].items():
                count = len(comments)
                percentage = count / len(self.comments) * 100 if self.comments else 0
                stats["情感分布"][sentiment] = {
                    "数量": count,
                    "占比": f"{percentage:.1f}%"
                }
        
        # 热度统计
        if self.comments:
            votes = [c.get('votes', 0) for c in self.comments]
            stats["热度统计"] = {
                "最高有用数": max(votes) if votes else 0,
                "平均有用数": f"{sum(votes) / len(votes):.1f}" if votes else 0,
                "有用数>100的评论": len([v for v in votes if v > 100]),
                "有用数>1000的评论": len([v for v in votes if v > 1000])
            }
        
        # 高频词统计
        stats["关键词统计"] = self._extract_keywords()
        
        self.statistics = stats
        return stats
    
    def _extract_keywords(self, top_n: int = 20) -> Dict[str, int]:
        """
        提取高频关键词
        
        Args:
            top_n: 返回的关键词数量
            
        Returns:
            关键词及其频次
        """
        if not SnowNLP:
            return {}
        
        all_text = ' '.join([c.get('content', '') for c in self.comments])
        
        if not all_text:
            return {}
        
        try:
            s = SnowNLP(all_text)
            # 获取关键词
            keywords = s.keywords(top_n)
            
            # 统计词频
            word_counter = Counter()
            for comment in self.comments:
                content = comment.get('content', '')
                for keyword in keywords:
                    if keyword in content:
                        word_counter[keyword] += content.count(keyword)
            
            return dict(word_counter.most_common(top_n))
            
        except Exception as e:
            print(f"关键词提取出错: {e}")
            return {}
    
    def get_sample_comments(self, category: str, n: int = 5) -> List[Dict]:
        """
        获取各分类的示例评论
        
        Args:
            category: 分类名称
            n: 示例数量
            
        Returns:
            示例评论列表
        """
        if 'by_rating' in self.classified_data and category in self.classified_data['by_rating']:
            comments = self.classified_data['by_rating'][category]
            # 按有用数排序，取最热门的
            sorted_comments = sorted(comments, key=lambda x: x.get('votes', 0), reverse=True)
            return sorted_comments[:n]
        
        if 'by_sentiment' in self.classified_data and category in self.classified_data['by_sentiment']:
            comments = self.classified_data['by_sentiment'][category]
            sorted_comments = sorted(comments, key=lambda x: x.get('votes', 0), reverse=True)
            return sorted_comments[:n]
        
        return []
    
    def print_summary(self):
        """打印分类摘要"""
        if not self.statistics:
            self.generate_statistics()
        
        print("\n" + "="*60)
        print("📊 评论统计摘要")
        print("="*60)
        
        # 总数
        print(f"\n📝 总评论数:")
        print(f"   短评: {self.statistics['总评论数']['短评']} 条")
        print(f"   长评: {self.statistics['总评论数']['长评']} 条")
        
        # 评分分布
        print(f"\n⭐ 评分分布:")
        if "详细评分" in self.statistics:
            for rating, data in self.statistics["详细评分"].items():
                bar = "█" * int(float(data['占比'].rstrip('%')) / 5)
                print(f"   {rating}: {data['数量']:>5} ({data['占比']:>5}) {bar}")
        
        # 情感分布
        print(f"\n😊 情感分布:")
        if "情感分布" in self.statistics:
            emoji_map = {"正面": "😊", "中性": "😐", "负面": "😢"}
            for sentiment, data in self.statistics["情感分布"].items():
                emoji = emoji_map.get(sentiment, "")
                bar = "█" * int(float(data['占比'].rstrip('%')) / 5)
                print(f"   {emoji} {sentiment}: {data['数量']:>5} ({data['占比']:>5}) {bar}")
        
        # 热门关键词
        print(f"\n🔑 热门关键词:")
        if "关键词统计" in self.statistics and self.statistics["关键词统计"]:
            keywords = list(self.statistics["关键词统计"].items())[:10]
            print("   " + ", ".join([f"{k}({v})" for k, v in keywords]))
        
        # 示例评论
        print(f"\n📌 各分类热门评论示例:")
        for category in ["好评", "差评"]:
            samples = self.get_sample_comments(category, 2)
            if samples:
                print(f"\n   【{category}】")
                for i, sample in enumerate(samples, 1):
                    content = sample.get('content', '')[:50] + "..." if len(sample.get('content', '')) > 50 else sample.get('content', '')
                    print(f"   {i}. {content} (👍{sample.get('votes', 0)})")
    
    def save_results(self):
        """保存分类结果和统计数据"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 保存统计数据
        stats_file = os.path.join(DATA_DIR, OUTPUT_STATS_JSON)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.statistics, f, ensure_ascii=False, indent=2)
        print(f"\n统计数据已保存到: {stats_file}")
        
        # 保存分类结果（只保存摘要，完整数据太大）
        classified_summary = {}
        for classify_type, data in self.classified_data.items():
            classified_summary[classify_type] = {}
            for category, comments in data.items():
                classified_summary[classify_type][category] = {
                    "count": len(comments),
                    "samples": [
                        {
                            "content": c.get('content', '')[:100],
                            "rating": c.get('rating', 0),
                            "votes": c.get('votes', 0)
                        }
                        for c in sorted(comments, key=lambda x: x.get('votes', 0), reverse=True)[:5]
                    ]
                }
        
        classified_file = os.path.join(DATA_DIR, OUTPUT_CLASSIFIED_JSON)
        with open(classified_file, 'w', encoding='utf-8') as f:
            json.dump(classified_summary, f, ensure_ascii=False, indent=2)
        print(f"分类结果已保存到: {classified_file}")
        
        # 保存带情感标注的完整数据
        if self.comments:
            df = pd.DataFrame(self.comments)
            sentiment_file = os.path.join(DATA_DIR, 'comments_with_sentiment.csv')
            df.to_csv(sentiment_file, index=False, encoding='utf-8-sig')
            print(f"带情感标注的评论已保存到: {sentiment_file}")


# 测试代码
if __name__ == "__main__":
    # 测试分类器
    classifier = CommentClassifier()
    
    # 从文件加载数据
    comments_file = os.path.join(DATA_DIR, 'comments.csv')
    reviews_file = os.path.join(DATA_DIR, 'reviews.csv')
    
    if os.path.exists(comments_file):
        classifier.load_from_csv(comments_file, reviews_file)
        classifier.classify_all()
        classifier.generate_statistics()
        classifier.print_summary()
        classifier.save_results()
    else:
        print("请先运行爬虫获取数据")
