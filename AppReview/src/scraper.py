"""
App Store 评论爬虫模块
负责从 iTunes API 获取应用信息和评论数据
"""
import requests
import time
import random
from typing import List, Dict, Optional, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SEARCH_API_URL, RSS_FEED_URL, HEADERS,
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, REQUEST_TIMEOUT,
    MAX_RETRIES, MAX_PAGES, PLATFORMS, COUNTRY
)


class AppStoreScraper:
    """App Store 评论爬虫"""
    
    def __init__(self, country: str = COUNTRY):
        self.country = country
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def _random_delay(self):
        """随机延迟，避免请求过快"""
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
    
    def _make_request(self, url: str, params: dict = None) -> Optional[dict]:
        """发送请求，带重试机制"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return None  # 页面不存在，正常情况
                print(f"    HTTP错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except requests.exceptions.RequestException as e:
                print(f"    请求错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except ValueError as e:
                print(f"    JSON解析错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def search_app(self, app_name: str, entity: str = "software") -> List[Dict]:
        """
        搜索应用，获取应用信息
        
        Args:
            app_name: 应用名称
            entity: 应用类型 (software=iOS/iPadOS, macSoftware=macOS)
        
        Returns:
            应用信息列表
        """
        params = {
            "term": app_name,
            "country": self.country,
            "entity": entity,
            "limit": 20
        }
        
        data = self._make_request(SEARCH_API_URL, params)
        if not data:
            return []
        
        results = []
        for app in data.get("results", []):
            results.append({
                "trackId": app.get("trackId"),
                "trackName": app.get("trackName"),
                "bundleId": app.get("bundleId"),
                "sellerName": app.get("sellerName"),
                "version": app.get("version"),
                "primaryGenreName": app.get("primaryGenreName"),
                "averageUserRating": app.get("averageUserRating"),
                "userRatingCount": app.get("userRatingCount"),
                "description": app.get("description", "")[:200],  # 截取描述前200字
                "artworkUrl100": app.get("artworkUrl100"),
                "releaseDate": app.get("releaseDate"),
                "currentVersionReleaseDate": app.get("currentVersionReleaseDate"),
            })
        
        return results
    
    def get_reviews(self, app_id: int, max_pages: int = MAX_PAGES, sort_by: str = "mostRecent") -> List[Dict]:
        """
        获取应用评论
        
        Args:
            app_id: 应用 ID (trackId)
            max_pages: 最大爬取页数 (最多10页)
            sort_by: 排序方式 (mostRecent/mostHelpful)
        
        Returns:
            评论列表
        """
        all_reviews = []
        max_pages = min(max_pages, MAX_PAGES)  # 确保不超过10页
        
        for page in range(1, max_pages + 1):
            url = RSS_FEED_URL.format(
                country=self.country,
                page=page,
                app_id=app_id,
                sort=sort_by
            )
            
            self._random_delay()
            data = self._make_request(url)
            
            if not data:
                print(f"    第 {page} 页无数据，停止爬取")
                break
            
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            
            if not entries:
                print(f"    第 {page} 页没有更多评论")
                break
            
            page_reviews = []
            for entry in entries:
                # 跳过应用信息条目（没有author字段）
                if "author" not in entry:
                    continue
                
                review = {
                    "id": entry.get("id", {}).get("label", ""),
                    "title": entry.get("title", {}).get("label", ""),
                    "content": entry.get("content", {}).get("label", ""),
                    "rating": int(entry.get("im:rating", {}).get("label", 0)),
                    "version": entry.get("im:version", {}).get("label", ""),
                    "author": entry.get("author", {}).get("name", {}).get("label", ""),
                    "author_uri": entry.get("author", {}).get("uri", {}).get("label", ""),
                    "updated": entry.get("updated", {}).get("label", ""),
                }
                page_reviews.append(review)
            
            all_reviews.extend(page_reviews)
            print(f"    第 {page} 页获取了 {len(page_reviews)} 条评论")
            
            # 如果这一页评论少于预期，可能已经到达最后
            if len(page_reviews) < 10:
                break
        
        return all_reviews
    
    def scrape_all_platforms(self, app_name: str) -> Dict[str, Dict]:
        """
        爬取所有平台的应用评论
        
        Args:
            app_name: 应用名称
        
        Returns:
            各平台的应用信息和评论数据
        """
        results = {}
        
        for platform_name, entity in PLATFORMS.items():
            print(f"\n🔍 正在搜索 {platform_name} 平台的 '{app_name}'...")
            
            apps = self.search_app(app_name, entity)
            
            if not apps:
                print(f"  ⚠️ 未找到相关应用")
                continue
            
            # 精确匹配目标应用名称
            target_apps = [app for app in apps if app.get("trackName", "") == app_name]
            
            if not target_apps:
                # 如果没有精确匹配，尝试包含匹配
                target_apps = [app for app in apps if app_name in app.get("trackName", "")]
            
            if not target_apps:
                print(f"  ⚠️ 未找到 '{app_name}'，跳过此平台")
                continue
            
            # 只取第一个匹配的应用
            for app in target_apps[:1]:
                app_id = app["trackId"]
                track_name = app["trackName"]
                
                print(f"\n📱 [{platform_name}] {track_name}")
                print(f"   App ID: {app_id}")
                print(f"   开发商: {app.get('sellerName', 'N/A')}")
                print(f"   评分: {app.get('averageUserRating', 'N/A')} ({app.get('userRatingCount', 0)} 个评分)")
                print(f"   版本: {app.get('version', 'N/A')}")
                
                print(f"   正在爬取评论...")
                reviews = self.get_reviews(app_id)
                
                key = f"{platform_name}"
                results[key] = {
                    "app_info": app,
                    "reviews": reviews,
                    "platform": platform_name
                }
                
                print(f"   ✅ 共获取 {len(reviews)} 条评论")
        
        return results
    
    def close(self):
        """关闭会话"""
        self.session.close()


if __name__ == "__main__":
    # 测试
    scraper = AppStoreScraper()
    results = scraper.scrape_all_platforms("小米互联服务")
    scraper.close()
    
    for platform, data in results.items():
        print(f"\n{platform}: {len(data['reviews'])} 条评论")
