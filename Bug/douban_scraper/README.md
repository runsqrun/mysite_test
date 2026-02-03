# 豆瓣电影评论爬虫 & 分析工具 🎬

爬取豆瓣电影的所有评论（短评+长评），并进行分类统计和情感分析。

## 目标电影
https://movie.douban.com/subject/36176155/

## 功能特点

- ✅ 自动爬取电影短评和长评
- ✅ 绕过豆瓣反爬虫机制（使用 undetected-chromedriver）
- ✅ 支持登录状态保持（Cookie管理）
- ✅ 按评分分类（好评/中评/差评）
- ✅ 情感分析（正面/中性/负面）
- ✅ 热度排序（按"有用"数）
- ✅ 关键词提取
- ✅ 数据导出（CSV/JSON）

## 安装依赖

```bash
cd douban_scraper
pip install -r requirements.txt
```

### 依赖说明
- `selenium` + `undetected-chromedriver`: 自动化浏览器，绕过反爬虫
- `beautifulsoup4`: HTML解析
- `pandas`: 数据处理
- `snownlp`: 中文情感分析
- `tqdm`: 进度条

## 使用方法

### 1. 首次运行 - 登录豆瓣
```bash
python main.py --login
```
这会打开浏览器，请手动登录豆瓣账号。登录后Cookie会自动保存。

### 2. 爬取评论
```bash
# 爬取所有评论（可能需要很长时间）
python main.py --scrape

# 只爬取前5页
python main.py --scrape --pages 5
```

### 3. 分析数据
```bash
python main.py --analyze
```

### 4. 一键完成（爬取+分析）
```bash
python main.py --all --pages 10
```

## 输出文件

所有输出保存在 `data/` 目录：

| 文件 | 说明 |
|------|------|
| `comments.csv` | 短评原始数据 |
| `reviews.csv` | 长评原始数据 |
| `movie_info.json` | 电影基本信息 |
| `statistics.json` | 统计摘要 |
| `classified_comments.json` | 分类结果 |
| `comments_with_sentiment.csv` | 带情感标注的评论 |

## 项目结构

```
douban_scraper/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表
├── README.md               # 说明文档
├── config/
│   └── settings.py         # 配置文件
├── src/
│   ├── scraper.py          # 爬虫核心
│   ├── parser.py           # HTML解析器
│   └── classifier.py       # 评论分类器
└── data/                   # 数据输出目录
    └── cookies.json        # 登录Cookie（自动生成）
```

## 配置说明

编辑 `config/settings.py` 可自定义：

```python
# 爬取频率（秒）
REQUEST_DELAY_MIN = 5
REQUEST_DELAY_MAX = 10

# 是否显示浏览器窗口
HEADLESS = False

# 情感分析阈值
SENTIMENT_POSITIVE_THRESHOLD = 0.6
SENTIMENT_NEGATIVE_THRESHOLD = 0.4
```

## 注意事项

⚠️ **反爬虫提醒**：
- 豆瓣有严格的反爬虫机制，请控制爬取频率
- 建议每次请求间隔 5-10 秒
- 如遇验证码，会提示手动处理

⚠️ **法律声明**：
- 本工具仅供学习研究使用
- 请遵守豆瓣用户协议和robots.txt
- 请勿用于商业目的或大规模数据采集

## 示例输出

```
📊 评论统计摘要
============================================
📝 总评论数:
   短评: 12345 条
   长评: 567 条

⭐ 评分分布:
   5星 (力荐):  5000 (40.5%) ████████
   4星 (推荐):  4000 (32.4%) ██████
   3星 (还行):  2000 (16.2%) ███
   2星 (较差):   800 ( 6.5%) █
   1星 (很差):   545 ( 4.4%) █

😊 情感分布:
   😊 正面:  8500 (68.8%) █████████████
   😐 中性:  2500 (20.3%) ████
   😢 负面:  1345 (10.9%) ██
```

## 常见问题

**Q: 提示"检测到安全验证"怎么办？**
A: 在弹出的浏览器中完成验证码，然后回车继续。

**Q: 爬取速度很慢？**
A: 这是为了避免被封禁。可以在settings.py中调低延迟，但不建议。

**Q: 如何更换目标电影？**
A: 修改 `config/settings.py` 中的 `MOVIE_ID` 和 `MOVIE_URL`。
