"""
豆瓣电影爬虫核心模块
使用Selenium + undetected-chromedriver绕过反爬虫机制
"""
import json
import os
import random
import time
from typing import List, Dict, Optional
from tqdm import tqdm

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("请先安装依赖: pip install undetected-chromedriver selenium")
    raise

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    MOVIE_URL, MOVIE_ID,
    COMMENTS_URL_TEMPLATE, REVIEWS_URL_TEMPLATE,
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    COMMENTS_PER_PAGE, REVIEWS_PER_PAGE,
    MAX_COMMENT_PAGES, MAX_REVIEW_PAGES,
    MAX_RETRIES, REQUEST_TIMEOUT,
    HEADLESS, USER_AGENT, COOKIE_FILE,
    DATA_DIR
)
from src.parser import DoubanParser


class DoubanScraper:
    """豆瓣电影爬虫"""
    
    def __init__(self, headless: bool = None):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式，None时使用配置文件设置
        """
        self.headless = headless if headless is not None else HEADLESS
        self.driver = None
        self.parser = DoubanParser()
        self.movie_info = {}
        self.comments = []
        self.reviews = []
    
    def _init_driver(self):
        """初始化Chrome浏览器驱动"""
        print("正在初始化浏览器...")
        
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # 基本配置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={USER_AGENT}')
        options.add_argument('--window-size=1920,1080')
        
        # 禁用自动化检测
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            # 自动检测Chrome版本并下载匹配的chromedriver
            self.driver = uc.Chrome(options=options, version_main=143)
            self.driver.implicitly_wait(10)
            print("浏览器初始化成功")
        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            raise
    
    def _random_delay(self):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
    
    def _save_cookies(self):
        """保存Cookie到文件"""
        if self.driver:
            cookies = self.driver.get_cookies()
            os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"Cookie已保存到: {COOKIE_FILE}")
    
    def _load_cookies(self) -> bool:
        """
        从文件加载Cookie
        
        Returns:
            是否成功加载
        """
        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                # 先访问豆瓣主页
                self.driver.get("https://www.douban.com")
                time.sleep(2)
                
                # 添加Cookie
                for cookie in cookies:
                    try:
                        # 移除可能导致问题的字段
                        cookie.pop('sameSite', None)
                        cookie.pop('expiry', None)
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"添加Cookie失败: {e}")
                
                print("Cookie加载成功")
                return True
            except Exception as e:
                print(f"加载Cookie失败: {e}")
        return False
    
    def login_manual(self):
        """
        手动登录豆瓣
        
        打开登录页面，等待用户手动登录，然后保存Cookie
        """
        if not self.driver:
            self._init_driver()
        
        print("\n" + "="*50)
        print("请在浏览器中手动登录豆瓣账号")
        print("登录成功后，在控制台输入 'done' 并回车")
        print("="*50 + "\n")
        
        # 打开登录页面
        self.driver.get("https://accounts.douban.com/passport/login")
        
        # 等待用户输入
        while True:
            user_input = input("登录完成请输入 'done': ").strip().lower()
            if user_input == 'done':
                break
        
        # 保存Cookie
        self._save_cookies()
        print("登录状态已保存，下次运行将自动使用")
    
    def start(self):
        """启动爬虫"""
        if not self.driver:
            self._init_driver()
        
        # 尝试加载已保存的Cookie
        self._load_cookies()
    
    def stop(self):
        """停止爬虫，关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("浏览器已关闭")
    
    def _get_page(self, url: str, retry: int = 0) -> Optional[str]:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            retry: 当前重试次数
            
        Returns:
            页面HTML内容或None
        """
        try:
            # 检查浏览器是否还活着
            try:
                _ = self.driver.current_url
            except:
                print("\n⚠️  浏览器窗口已关闭，正在重新初始化...")
                self._init_driver()
                self._load_cookies()
            
            self.driver.get(url)
            self._random_delay()
            
            # 检查是否被重定向到安全验证页面
            current_url = self.driver.current_url
            if 'sec.douban.com' in current_url:
                print("\n⚠️  检测到安全验证，请在浏览器中完成验证...")
                input("完成验证后按回车继续...")
                self.driver.get(url)
                self._random_delay()
            
            # 等待页面加载
            WebDriverWait(self.driver, REQUEST_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return self.driver.page_source
            
        except TimeoutException:
            print(f"页面加载超时: {url}")
            if retry < MAX_RETRIES:
                print(f"重试 ({retry + 1}/{MAX_RETRIES})...")
                self._random_delay()
                return self._get_page(url, retry + 1)
            return None
            
        except WebDriverException as e:
            print(f"浏览器错误: {e}")
            # 如果是窗口关闭错误，尝试重新初始化
            if "no such window" in str(e) or "target window already closed" in str(e):
                print("\n⚠️  浏览器窗口已关闭，正在重新初始化...")
                try:
                    self._init_driver()
                    self._load_cookies()
                    if retry < MAX_RETRIES:
                        return self._get_page(url, retry + 1)
                except Exception as init_error:
                    print(f"重新初始化失败: {init_error}")
            elif retry < MAX_RETRIES:
                print(f"重试 ({retry + 1}/{MAX_RETRIES})...")
                self._random_delay()
                return self._get_page(url, retry + 1)
            return None
    
    def scrape_movie_info(self) -> Dict:
        """
        爬取电影基本信息
        
        Returns:
            电影信息字典
        """
        print(f"\n正在获取电影信息: {MOVIE_URL}")
        
        html = self._get_page(MOVIE_URL)
        if html:
            self.movie_info = self.parser.parse_movie_info(html)
            print(f"电影: {self.movie_info.get('title', '未知')}")
            print(f"评分: {self.movie_info.get('rating', 0)}")
            print(f"评价人数: {self.movie_info.get('votes', 0)}")
        else:
            print("获取电影信息失败")
        
        return self.movie_info
    
    def scrape_comments(self, max_pages: int = None) -> List[Dict]:
        """
        爬取所有短评
        
        Args:
            max_pages: 最大爬取页数，None表示爬取全部
            
        Returns:
            短评列表
        """
        print("\n" + "="*50)
        print("开始爬取短评...")
        print("="*50)
        
        max_pages = max_pages or MAX_COMMENT_PAGES
        page = 0
        total_comments = []
        
        # 获取第一页，确定总数
        first_url = COMMENTS_URL_TEMPLATE.format(movie_id=MOVIE_ID, start=0)
        html = self._get_page(first_url)
        
        if not html:
            print("获取短评页面失败")
            return total_comments
        
        total_count = self.parser.get_total_comments_count(html)
        total_pages = (total_count + COMMENTS_PER_PAGE - 1) // COMMENTS_PER_PAGE if total_count > 0 else 1
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        print(f"预计爬取 {total_pages} 页，共约 {total_count} 条短评")
        
        # 使用进度条
        with tqdm(total=total_pages, desc="爬取短评") as pbar:
            while True:
                start = page * COMMENTS_PER_PAGE
                url = COMMENTS_URL_TEMPLATE.format(movie_id=MOVIE_ID, start=start)
                
                if page > 0:  # 第一页已经获取过了
                    html = self._get_page(url)
                
                if not html:
                    print(f"\n第 {page + 1} 页获取失败，跳过")
                    page += 1
                    pbar.update(1)
                    continue
                
                comments = self.parser.parse_comments_page(html)
                
                if not comments:
                    print(f"\n第 {page + 1} 页没有评论，可能已到末尾")
                    break
                
                total_comments.extend(comments)
                pbar.update(1)
                pbar.set_postfix({"已获取": len(total_comments)})
                
                page += 1
                
                # 检查是否达到最大页数
                if max_pages and page >= max_pages:
                    break
                
                # 检查是否有下一页
                if not self.parser.has_next_page(html):
                    break
        
        self.comments = total_comments
        print(f"\n短评爬取完成，共获取 {len(total_comments)} 条")
        
        return total_comments
    
    def scrape_reviews(self, max_pages: int = None) -> List[Dict]:
        """
        爬取所有长评（影评）
        
        Args:
            max_pages: 最大爬取页数，None表示爬取全部
            
        Returns:
            影评列表
        """
        print("\n" + "="*50)
        print("开始爬取长评（影评）...")
        print("="*50)
        
        max_pages = max_pages or MAX_REVIEW_PAGES
        page = 0
        total_reviews = []
        
        # 获取第一页
        first_url = REVIEWS_URL_TEMPLATE.format(movie_id=MOVIE_ID, start=0)
        html = self._get_page(first_url)
        
        if not html:
            print("获取影评页面失败")
            return total_reviews
        
        total_count = self.parser.get_total_reviews_count(html)
        total_pages = (total_count + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE if total_count > 0 else 1
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        print(f"预计爬取 {total_pages} 页，共约 {total_count} 条影评")
        
        with tqdm(total=total_pages, desc="爬取影评") as pbar:
            while True:
                start = page * REVIEWS_PER_PAGE
                url = REVIEWS_URL_TEMPLATE.format(movie_id=MOVIE_ID, start=start)
                
                if page > 0:
                    html = self._get_page(url)
                
                if not html:
                    print(f"\n第 {page + 1} 页获取失败，跳过")
                    page += 1
                    pbar.update(1)
                    continue
                
                reviews = self.parser.parse_reviews_page(html)
                
                if not reviews:
                    print(f"\n第 {page + 1} 页没有影评，可能已到末尾")
                    break
                
                total_reviews.extend(reviews)
                pbar.update(1)
                pbar.set_postfix({"已获取": len(total_reviews)})
                
                page += 1
                
                if max_pages and page >= max_pages:
                    break
                
                if not self.parser.has_next_page(html):
                    break
        
        self.reviews = total_reviews
        print(f"\n影评爬取完成，共获取 {len(total_reviews)} 条")
        
        return total_reviews
    
    def scrape_all(self, max_comment_pages: int = None, max_review_pages: int = None) -> Dict:
        """
        爬取所有数据（电影信息、短评、长评）
        
        Args:
            max_comment_pages: 短评最大页数
            max_review_pages: 长评最大页数
            
        Returns:
            包含所有数据的字典
        """
        self.start()
        
        try:
            # 爬取电影信息
            self.scrape_movie_info()
            
            # 爬取短评
            self.scrape_comments(max_comment_pages)
            
            # 爬取长评
            self.scrape_reviews(max_review_pages)
            
            return {
                'movie_info': self.movie_info,
                'comments': self.comments,
                'reviews': self.reviews
            }
            
        finally:
            self.stop()
    
    def save_raw_data(self):
        """保存原始数据到文件"""
        import pandas as pd
        
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 保存短评
        if self.comments:
            comments_file = os.path.join(DATA_DIR, 'comments.csv')
            df_comments = pd.DataFrame(self.comments)
            df_comments.to_csv(comments_file, index=False, encoding='utf-8-sig')
            print(f"短评已保存到: {comments_file}")
        
        # 保存影评
        if self.reviews:
            reviews_file = os.path.join(DATA_DIR, 'reviews.csv')
            df_reviews = pd.DataFrame(self.reviews)
            df_reviews.to_csv(reviews_file, index=False, encoding='utf-8-sig')
            print(f"影评已保存到: {reviews_file}")
        
        # 保存电影信息
        if self.movie_info:
            info_file = os.path.join(DATA_DIR, 'movie_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(self.movie_info, f, ensure_ascii=False, indent=2)
            print(f"电影信息已保存到: {info_file}")


# 测试代码
if __name__ == "__main__":
    scraper = DoubanScraper(headless=False)
    
    # 如果需要登录，取消下面的注释
    # scraper.login_manual()
    
    # 测试爬取（只爬取1页）
    data = scraper.scrape_all(max_comment_pages=1, max_review_pages=1)
    scraper.save_raw_data()
