"""
小米互联服务 App Store 评论爬取与分析工具
主程序入口
"""
import argparse
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, COUNTRY, DATA_DIR
from src.scraper import AppStoreScraper
from src.parser import ReviewParser
from src.classifier import ReviewClassifier


def print_separator(char="=", length=70):
    """打印分隔线"""
    print(char * length)


def print_rating_bar(count: int, total: int, bar_length: int = 20) -> str:
    """生成评分条形图"""
    if total == 0:
        return ""
    percentage = count / total
    filled = int(bar_length * percentage)
    bar = "█" * filled + "░" * (bar_length - filled)
    return f"{bar} {count:3d} ({percentage * 100:5.1f}%)"


def print_analysis_report(analysis: dict, platform: str):
    """打印分析报告"""
    print_separator("=")
    print(f"📱 {platform} 平台分析报告")
    print_separator("=")
    
    summary = analysis.get("summary", {})
    total = summary.get("total_reviews", 0)
    avg_rating = summary.get("average_rating", 0)
    rating_dist = summary.get("rating_distribution", {})
    
    # 评分分布
    print(f"\n⭐ 评分分布 (共 {total} 条评论，平均 {avg_rating:.2f} 星)")
    print("-" * 50)
    for star in range(5, 0, -1):
        count = rating_dist.get(star, 0)
        bar = print_rating_bar(count, total)
        print(f"  {star} 星: {bar}")
    
    # 按评分分类
    print(f"\n📊 评分分类统计")
    print("-" * 50)
    by_rating = analysis.get("by_rating", {})
    for category, data in by_rating.items():
        count = data.get("count", 0)
        pct = data.get("percentage", 0)
        print(f"  {category}: {count} 条 ({pct}%)")
    
    # 按关键词分类
    print(f"\n📁 问题类型分类")
    print("-" * 50)
    by_keywords = analysis.get("by_keywords", {})
    for category, data in sorted(by_keywords.items(), key=lambda x: x[1].get("count", 0), reverse=True):
        count = data.get("count", 0)
        if count > 0:
            pct = data.get("percentage", 0)
            print(f"  {category}: {count} 条 ({pct}%)")
    
    # 按情感分类
    print(f"\n😊 情感分析")
    print("-" * 50)
    by_sentiment = analysis.get("by_sentiment", {})
    sentiment_emoji = {"正面": "😊", "中性": "😐", "负面": "😞"}
    for sentiment, data in by_sentiment.items():
        count = data.get("count", 0)
        pct = data.get("percentage", 0)
        emoji = sentiment_emoji.get(sentiment, "")
        print(f"  {emoji} {sentiment}: {count} 条 ({pct}%)")
    
    # 高频词统计
    print(f"\n🔤 高频词 Top 15")
    print("-" * 50)
    word_freq = analysis.get("word_frequency", [])[:15]
    for i, (word, count) in enumerate(word_freq, 1):
        bar = "▓" * min(count // 2, 20)
        print(f"  {i:2d}. {word:<8} {bar} ({count})")
    
    # TF-IDF 关键词
    print(f"\n🔑 TF-IDF 关键词 Top 10")
    print("-" * 50)
    keywords_tfidf = analysis.get("keywords_tfidf", [])[:10]
    for i, (word, weight) in enumerate(keywords_tfidf, 1):
        bar = "▓" * int(weight * 30)
        print(f"  {i:2d}. {word:<8} {bar} ({weight:.3f})")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小米互联服务 App Store 评论爬取与分析工具")
    parser.add_argument("--app", type=str, default=APP_NAME, help="应用名称")
    parser.add_argument("--country", type=str, default=COUNTRY, help="国家/地区代码")
    parser.add_argument("--pages", type=int, default=10, help="最大爬取页数 (最多10)")
    args = parser.parse_args()
    
    print_separator()
    print("🍎 App Store 评论爬取与分析工具")
    print_separator()
    print(f"📱 目标应用: {args.app}")
    print(f"🌍 地区: 中国大陆 ({args.country})")
    print(f"📄 最大页数: {args.pages}")
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # 初始化组件
    scraper = AppStoreScraper(country=args.country)
    review_parser = ReviewParser()
    classifier = ReviewClassifier()
    
    try:
        # Step 1: 爬取评论
        print("\n📥 开始爬取评论...")
        scrape_results = scraper.scrape_all_platforms(args.app)
        
        if not scrape_results:
            print("❌ 未获取到任何评论数据")
            return
        
        # Step 2: 解析评论
        print("\n📝 解析评论数据...")
        all_reviews = review_parser.parse_all_reviews(scrape_results)
        print(f"  共解析 {len(all_reviews)} 条评论")
        
        # Step 3: 保存原始数据
        print("\n💾 保存数据...")
        csv_path = review_parser.save_to_csv(all_reviews)
        print(f"  CSV 文件: {csv_path}")
        
        json_path = review_parser.save_to_json(all_reviews)
        print(f"  JSON 文件: {json_path}")
        
        app_info_path = review_parser.save_app_info(scrape_results)
        print(f"  应用信息: {app_info_path}")
        
        # Step 4: 分析评论
        print("\n📊 开始分析评论...")
        
        # 按平台分别分析
        all_analysis = {}
        for platform, data in scrape_results.items():
            platform_reviews = [r for r in all_reviews if r.get("platform") == data.get("platform")]
            if platform_reviews:
                analysis = classifier.analyze_all(platform_reviews)
                all_analysis[platform] = analysis
                print_analysis_report(analysis, platform)
        
        # 整体分析
        if len(scrape_results) > 1:
            print("\n")
            overall_analysis = classifier.analyze_all(all_reviews)
            all_analysis["overall"] = overall_analysis
            print_analysis_report(overall_analysis, "全平台汇总")
        
        # Step 5: 保存分析结果
        analysis_path = classifier.save_analysis(all_analysis)
        print(f"\n💾 分析结果已保存: {analysis_path}")
        
        # 打印示例评论
        print_separator()
        print("\n💬 评论示例")
        print_separator()
        
        for platform, data in scrape_results.items():
            print(f"\n📱 {platform}:")
            reviews = data.get("reviews", [])[:3]
            for i, review in enumerate(reviews, 1):
                stars = "⭐" * review.get("rating", 0)
                print(f"\n  [{i}] {stars}")
                print(f"      标题: {review.get('title', 'N/A')}")
                content = review.get("content", "")
                if len(content) > 100:
                    content = content[:100] + "..."
                print(f"      内容: {content}")
                print(f"      版本: {review.get('version', 'N/A')}")
        
        print_separator()
        print("✅ 爬取与分析完成!")
        print_separator()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
