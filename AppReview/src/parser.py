"""
评论解析模块
负责解析和转换评论数据格式
"""
import csv
import json
import os
from typing import List, Dict
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATA_DIR, OUTPUT_REVIEWS_CSV, OUTPUT_REVIEWS_JSON, OUTPUT_APP_INFO_JSON


class ReviewParser:
    """评论解析器"""
    
    def __init__(self):
        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def parse_review(self, raw_review: Dict, platform: str) -> Dict:
        """
        解析单条评论
        
        Args:
            raw_review: 原始评论数据
            platform: 平台名称
        
        Returns:
            格式化后的评论数据
        """
        return {
            "id": raw_review.get("id", ""),
            "platform": platform,
            "title": raw_review.get("title", ""),
            "content": raw_review.get("content", ""),
            "rating": raw_review.get("rating", 0),
            "version": raw_review.get("version", ""),
            "author": raw_review.get("author", ""),
            "updated": self._parse_date(raw_review.get("updated", "")),
            "full_text": f"{raw_review.get('title', '')} {raw_review.get('content', '')}".strip()
        }
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return ""
        try:
            # App Store 日期格式: 2024-01-15T10:30:00-07:00
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return date_str
    
    def parse_all_reviews(self, scrape_results: Dict) -> List[Dict]:
        """
        解析所有平台的评论
        
        Args:
            scrape_results: 爬虫返回的结果
        
        Returns:
            格式化后的评论列表
        """
        all_reviews = []
        
        for platform, data in scrape_results.items():
            platform_name = data.get("platform", platform)
            reviews = data.get("reviews", [])
            
            for review in reviews:
                parsed = self.parse_review(review, platform_name)
                all_reviews.append(parsed)
        
        return all_reviews
    
    def save_to_csv(self, reviews: List[Dict], filename: str = None) -> str:
        """
        保存评论到 CSV 文件
        
        Args:
            reviews: 评论列表
            filename: 文件名（可选）
        
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(DATA_DIR, filename or OUTPUT_REVIEWS_CSV)
        
        if not reviews:
            print("没有评论数据可保存")
            return filepath
        
        fieldnames = ["id", "platform", "title", "content", "rating", "version", "author", "updated"]
        
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(reviews)
        
        return filepath
    
    def save_to_json(self, reviews: List[Dict], filename: str = None) -> str:
        """
        保存评论到 JSON 文件
        
        Args:
            reviews: 评论列表
            filename: 文件名（可选）
        
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(DATA_DIR, filename or OUTPUT_REVIEWS_JSON)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def save_app_info(self, scrape_results: Dict, filename: str = None) -> str:
        """
        保存应用信息到 JSON 文件
        
        Args:
            scrape_results: 爬虫返回的结果
            filename: 文件名（可选）
        
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(DATA_DIR, filename or OUTPUT_APP_INFO_JSON)
        
        app_info = {}
        for platform, data in scrape_results.items():
            app_info[platform] = {
                "app_info": data.get("app_info", {}),
                "review_count": len(data.get("reviews", []))
            }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(app_info, f, ensure_ascii=False, indent=2)
        
        return filepath


if __name__ == "__main__":
    # 测试解析器
    parser = ReviewParser()
    
    # 测试数据
    test_data = {
        "iOS/iPadOS": {
            "app_info": {"trackName": "小米互联服务"},
            "platform": "iOS/iPadOS",
            "reviews": [
                {
                    "id": "123",
                    "title": "测试标题",
                    "content": "测试内容",
                    "rating": 5,
                    "version": "1.0",
                    "author": "测试用户",
                    "updated": "2024-01-15T10:30:00-07:00"
                }
            ]
        }
    }
    
    reviews = parser.parse_all_reviews(test_data)
    print(f"解析了 {len(reviews)} 条评论")
