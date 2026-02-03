"""
HTML解析器 - 解析豆瓣电影评论页面
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import RATING_MAP


class DoubanParser:
    """豆瓣页面解析器"""
    
    def __init__(self):
        pass
    
    def parse_movie_info(self, html: str) -> Dict:
        """
        解析电影基本信息
        
        Args:
            html: 电影主页HTML内容
            
        Returns:
            包含电影信息的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        info = {}
        
        # 电影标题
        title_elem = soup.find('span', property='v:itemreviewed')
        info['title'] = title_elem.get_text(strip=True) if title_elem else "未知"
        
        # 评分
        rating_elem = soup.find('strong', class_='rating_num')
        info['rating'] = float(rating_elem.get_text(strip=True)) if rating_elem else 0.0
        
        # 评价人数
        rating_people = soup.find('span', property='v:votes')
        info['votes'] = int(rating_people.get_text(strip=True)) if rating_people else 0
        
        # 导演
        directors = soup.find_all('a', rel='v:directedBy')
        info['directors'] = [d.get_text(strip=True) for d in directors]
        
        # 主演
        actors = soup.find_all('a', rel='v:starring')
        info['actors'] = [a.get_text(strip=True) for a in actors[:10]]  # 只取前10个
        
        # 类型
        genres = soup.find_all('span', property='v:genre')
        info['genres'] = [g.get_text(strip=True) for g in genres]
        
        # 上映日期
        release_date = soup.find('span', property='v:initialReleaseDate')
        info['release_date'] = release_date.get_text(strip=True) if release_date else "未知"
        
        # 简介
        summary_elem = soup.find('span', property='v:summary')
        info['summary'] = summary_elem.get_text(strip=True) if summary_elem else ""
        
        return info
    
    def parse_comments_page(self, html: str) -> List[Dict]:
        """
        解析短评页面
        
        Args:
            html: 短评页面HTML内容
            
        Returns:
            评论列表
        """
        soup = BeautifulSoup(html, 'lxml')
        comments = []
        
        # 查找所有评论项
        comment_items = soup.find_all('div', class_='comment-item')
        
        for item in comment_items:
            comment = self._parse_single_comment(item)
            if comment:
                comments.append(comment)
        
        return comments
    
    def _parse_single_comment(self, item) -> Optional[Dict]:
        """
        解析单条短评
        
        Args:
            item: BeautifulSoup评论元素
            
        Returns:
            评论字典或None
        """
        try:
            comment = {}
            
            # 用户名
            user_elem = item.find('span', class_='comment-info')
            if user_elem:
                user_link = user_elem.find('a')
                comment['username'] = user_link.get_text(strip=True) if user_link else "匿名"
                comment['user_url'] = user_link.get('href', '') if user_link else ""
            else:
                comment['username'] = "匿名"
                comment['user_url'] = ""
            
            # 评分
            rating_span = item.find('span', class_=re.compile(r'allstar\d+'))
            if rating_span:
                rating_class = [c for c in rating_span.get('class', []) if c.startswith('allstar')]
                if rating_class:
                    comment['rating'] = RATING_MAP.get(rating_class[0], 0)
                else:
                    comment['rating'] = 0
            else:
                comment['rating'] = 0
            
            # 评论时间
            time_elem = item.find('span', class_='comment-time')
            comment['time'] = time_elem.get('title', time_elem.get_text(strip=True)) if time_elem else ""
            
            # 评论内容
            content_elem = item.find('span', class_='short')
            comment['content'] = content_elem.get_text(strip=True) if content_elem else ""
            
            # 有用数（点赞数）
            vote_elem = item.find('span', class_='votes')
            if vote_elem:
                vote_text = vote_elem.get_text(strip=True)
                comment['votes'] = int(vote_text) if vote_text.isdigit() else 0
            else:
                comment['votes'] = 0
            
            # 评论ID
            comment_id = item.get('data-cid', '')
            comment['comment_id'] = comment_id
            
            return comment if comment['content'] else None
            
        except Exception as e:
            print(f"解析评论出错: {e}")
            return None
    
    def parse_reviews_page(self, html: str) -> List[Dict]:
        """
        解析长评（影评）列表页面
        
        Args:
            html: 长评列表页面HTML内容
            
        Returns:
            影评列表
        """
        soup = BeautifulSoup(html, 'lxml')
        reviews = []
        
        # 查找所有影评项
        review_items = soup.find_all('div', class_='review-item')
        
        for item in review_items:
            review = self._parse_single_review(item)
            if review:
                reviews.append(review)
        
        return reviews
    
    def _parse_single_review(self, item) -> Optional[Dict]:
        """
        解析单条长评
        
        Args:
            item: BeautifulSoup影评元素
            
        Returns:
            影评字典或None
        """
        try:
            review = {}
            
            # 用户名
            user_elem = item.find('a', class_='name')
            review['username'] = user_elem.get_text(strip=True) if user_elem else "匿名"
            review['user_url'] = user_elem.get('href', '') if user_elem else ""
            
            # 标题
            title_elem = item.find('h2')
            if title_elem:
                title_link = title_elem.find('a')
                review['title'] = title_link.get_text(strip=True) if title_link else ""
                review['review_url'] = title_link.get('href', '') if title_link else ""
            else:
                review['title'] = ""
                review['review_url'] = ""
            
            # 评分
            rating_span = item.find('span', class_=re.compile(r'allstar\d+'))
            if rating_span:
                rating_class = [c for c in rating_span.get('class', []) if c.startswith('allstar')]
                if rating_class:
                    review['rating'] = RATING_MAP.get(rating_class[0], 0)
                else:
                    review['rating'] = 0
            else:
                review['rating'] = 0
            
            # 发布时间
            time_elem = item.find('span', class_='main-meta')
            review['time'] = time_elem.get_text(strip=True) if time_elem else ""
            
            # 摘要内容
            content_elem = item.find('div', class_='short-content')
            if content_elem:
                # 移除"(展开)"文字
                content_text = content_elem.get_text(strip=True)
                content_text = re.sub(r'\(展开\)$', '', content_text).strip()
                review['summary'] = content_text
            else:
                review['summary'] = ""
            
            # 有用数
            useful_elem = item.find('a', class_='action-btn')
            if useful_elem:
                useful_text = useful_elem.get_text(strip=True)
                match = re.search(r'(\d+)', useful_text)
                review['useful_count'] = int(match.group(1)) if match else 0
            else:
                review['useful_count'] = 0
            
            # 回复数
            reply_elem = item.find('a', href=re.compile(r'#comments'))
            if reply_elem:
                reply_text = reply_elem.get_text(strip=True)
                match = re.search(r'(\d+)', reply_text)
                review['reply_count'] = int(match.group(1)) if match else 0
            else:
                review['reply_count'] = 0
            
            return review if review['title'] or review['summary'] else None
            
        except Exception as e:
            print(f"解析影评出错: {e}")
            return None
    
    def parse_full_review(self, html: str) -> Dict:
        """
        解析完整影评页面（单篇影评详情）
        
        Args:
            html: 影评详情页面HTML内容
            
        Returns:
            完整影评内容
        """
        soup = BeautifulSoup(html, 'lxml')
        review = {}
        
        # 标题
        title_elem = soup.find('h1')
        review['title'] = title_elem.get_text(strip=True) if title_elem else ""
        
        # 作者
        author_elem = soup.find('span', property='v:reviewer')
        review['author'] = author_elem.get_text(strip=True) if author_elem else ""
        
        # 完整内容
        content_elem = soup.find('div', class_='review-content')
        if content_elem:
            # 获取所有段落
            paragraphs = content_elem.find_all('p')
            review['content'] = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        else:
            review['content'] = ""
        
        return review
    
    def get_total_comments_count(self, html: str) -> int:
        """
        获取短评总数
        
        Args:
            html: 短评页面HTML内容
            
        Returns:
            评论总数
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 尝试从标签页获取
        tab_elem = soup.find('li', class_='is-active')
        if tab_elem:
            text = tab_elem.get_text()
            match = re.search(r'全部\s*(\d+)', text)
            if match:
                return int(match.group(1))
        
        # 尝试从其他位置获取
        count_elem = soup.find('div', class_='mod-hd')
        if count_elem:
            text = count_elem.get_text()
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
        
        return 0
    
    def get_total_reviews_count(self, html: str) -> int:
        """
        获取长评总数
        
        Args:
            html: 长评页面HTML内容
            
        Returns:
            影评总数
        """
        soup = BeautifulSoup(html, 'lxml')
        
        header = soup.find('header', class_='main-hd')
        if header:
            text = header.get_text()
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
        
        return 0
    
    def has_next_page(self, html: str) -> bool:
        """
        检查是否有下一页
        
        Args:
            html: 当前页面HTML内容
            
        Returns:
            是否有下一页
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 查找下一页链接
        next_link = soup.find('a', class_='next')
        if next_link:
            return True
        
        # 检查分页器
        paginator = soup.find('div', class_='paginator')
        if paginator:
            next_btn = paginator.find('span', class_='next')
            if next_btn and next_btn.find('a'):
                return True
        
        return False


# 测试代码
if __name__ == "__main__":
    parser = DoubanParser()
    print("Parser模块加载成功")
