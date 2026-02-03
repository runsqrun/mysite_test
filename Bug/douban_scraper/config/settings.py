"""
豆瓣电影爬虫配置文件
"""
import os

# ==================== 目标URL配置 ====================
# 电影主页
MOVIE_URL = "https://movie.douban.com/subject/36176155/"
MOVIE_ID = "36176155"

# 短评页面URL模板
COMMENTS_URL_TEMPLATE = "https://movie.douban.com/subject/{movie_id}/comments?start={start}&limit=20&status=P&sort=new_score"

# 长评页面URL模板
REVIEWS_URL_TEMPLATE = "https://movie.douban.com/subject/{movie_id}/reviews?start={start}"

# ==================== 爬虫行为配置 ====================
# 请求间隔（秒）- 为避免被封，建议5-10秒
REQUEST_DELAY_MIN = 5
REQUEST_DELAY_MAX = 10

# 每页评论数
COMMENTS_PER_PAGE = 20
REVIEWS_PER_PAGE = 10

# 最大爬取页数（设为None表示爬取全部）
MAX_COMMENT_PAGES = None  # 短评最大页数
MAX_REVIEW_PAGES = None   # 长评最大页数

# 重试次数
MAX_RETRIES = 3

# 请求超时（秒）
REQUEST_TIMEOUT = 30

# ==================== 浏览器配置 ====================
# 是否使用无头模式（不显示浏览器窗口）
HEADLESS = False  # 首次运行建议False，方便处理验证码

# Chrome浏览器路径（留空自动检测）
CHROME_PATH = ""

# User-Agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==================== Cookie配置 ====================
# Cookie文件路径（手动登录后保存）
COOKIE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "cookies.json")

# ==================== 数据存储配置 ====================
# 数据输出目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# 输出文件名
OUTPUT_COMMENTS_CSV = "comments.csv"
OUTPUT_REVIEWS_CSV = "reviews.csv"
OUTPUT_STATS_JSON = "statistics.json"
OUTPUT_CLASSIFIED_JSON = "classified_comments.json"

# ==================== 评分映射 ====================
RATING_MAP = {
    "allstar50": 5,  # 力荐
    "allstar40": 4,  # 推荐
    "allstar30": 3,  # 还行
    "allstar20": 2,  # 较差
    "allstar10": 1,  # 很差
}

RATING_TEXT_MAP = {
    5: "力荐",
    4: "推荐",
    3: "还行",
    2: "较差",
    1: "很差",
    0: "未评分"
}

# ==================== 分类配置 ====================
# 情感分析阈值
SENTIMENT_POSITIVE_THRESHOLD = 0.6  # 大于此值为正面
SENTIMENT_NEGATIVE_THRESHOLD = 0.4  # 小于此值为负面

# 评分分类
RATING_CATEGORIES = {
    "好评": [4, 5],
    "中评": [3],
    "差评": [1, 2],
    "未评分": [0]
}

# ==================== 日志配置 ====================
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "scraper.log")
