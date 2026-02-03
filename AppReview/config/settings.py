"""
App Store 评论爬虫配置文件
"""
import os

# ==================== 基本配置 ====================
APP_NAME = "小米互联服务"
COUNTRY = "cn"  # 中国大陆

# ==================== API 端点 ====================
# iTunes Search API - 搜索应用
SEARCH_API_URL = "https://itunes.apple.com/search"

# iTunes Lookup API - 查询特定应用
LOOKUP_API_URL = "https://itunes.apple.com/lookup"

# RSS Feed API - 获取评论
RSS_FEED_URL = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby={sort}/json"

# ==================== 平台配置 ====================
# entity 参数用于区分平台
PLATFORMS = {
    "iOS/iPadOS": "software",      # iPhone/iPad 应用
    "macOS": "macSoftware",        # Mac 应用
}

# ==================== 请求配置 ====================
REQUEST_DELAY_MIN = 1.0  # 最小请求延迟（秒）
REQUEST_DELAY_MAX = 3.0  # 最大请求延迟（秒）
REQUEST_TIMEOUT = 30     # 请求超时（秒）
MAX_RETRIES = 3          # 最大重试次数
MAX_PAGES = 10           # RSS Feed 最大页数（硬限制）

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ==================== 评分分类配置 ====================
RATING_CATEGORIES = {
    "好评": [4, 5],
    "中评": [3],
    "差评": [1, 2],
}

# 情感分析阈值
SENTIMENT_POSITIVE_THRESHOLD = 0.6
SENTIMENT_NEGATIVE_THRESHOLD = 0.4

# ==================== 关键词分类配置 ====================
KEYWORD_CATEGORIES = {
    "功能问题": ["功能", "不能", "无法", "失败", "不支持", "缺少", "没有", "不行", "用不了", "bug", "BUG"],
    "连接问题": ["连接", "断开", "连不上", "断连", "蓝牙", "wifi", "WiFi", "网络", "配对", "识别不到", "搜索不到", "找不到"],
    "界面体验": ["界面", "UI", "设计", "美观", "简洁", "复杂", "难用", "操作", "交互", "丑", "好看"],
    "性能问题": ["卡顿", "慢", "卡", "闪退", "崩溃", "耗电", "发热", "内存", "性能", "占用"],
    "更新问题": ["更新", "版本", "升级", "新版", "旧版", "回退", "适配"],
    "设备兼容": ["小米", "红米", "手环", "手表", "耳机", "音箱", "电视", "路由器", "摄像头", "门锁", "空调"],
}

# ==================== 停用词配置 ====================
STOPWORDS = [
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "那", "还", "能", "它", "与", "吗", "什么", "让", "但", "为",
    "以", "被", "给", "等", "这个", "那个", "可以", "只", "又", "其", "把", "因为",
    "所以", "而", "之", "或", "如果", "但是", "就是", "用", "呢", "啊", "吧", "啦",
    "么", "哦", "嗯", "哎", "呀", "哈", "嘛", "哪", "怎么", "为什么", "这样", "那样",
    "app", "App", "APP", "iphone", "iPhone", "ipad", "iPad", "mac", "Mac",
    "iOS", "ios", "软件", "应用", "下载", "使用", "手机", "平板", "电脑",
    "真的", "感觉", "希望", "建议", "时候", "问题", "东西", "事情", "觉得",
]

# ==================== 数据存储配置 ====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 输出文件名
OUTPUT_REVIEWS_CSV = "reviews.csv"
OUTPUT_REVIEWS_JSON = "reviews.json"
OUTPUT_ANALYSIS_JSON = "analysis.json"
OUTPUT_APP_INFO_JSON = "app_info.json"
