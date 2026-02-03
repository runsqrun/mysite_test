#!/usr/bin/env python3
"""
豆瓣电影评论爬虫 - 主程序
爬取豆瓣电影的所有评论，并进行分类统计

目标电影: https://movie.douban.com/subject/36176155/

使用方法:
    1. 首次运行需要登录: python main.py --login
    2. 爬取所有数据: python main.py --scrape
    3. 只分析已有数据: python main.py --analyze
    4. 完整流程: python main.py --all
"""
import argparse
import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.scraper import DoubanScraper
from src.classifier import CommentClassifier
from config.settings import DATA_DIR, MOVIE_URL


def print_banner():
    """打印欢迎信息"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          🎬 豆瓣电影评论爬虫 & 分析工具 🎬               ║
    ║                                                          ║
    ║   功能: 爬取电影评论 | 情感分析 | 评分统计 | 分类整理    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    目标电影: {MOVIE_URL}\n")


def login():
    """手动登录豆瓣"""
    print("\n📝 启动登录模式...")
    print("=" * 50)
    
    scraper = DoubanScraper(headless=False)
    try:
        scraper.login_manual()
        print("\n✅ 登录成功！Cookie已保存，下次运行将自动使用。")
    except Exception as e:
        print(f"\n❌ 登录失败: {e}")
    finally:
        scraper.stop()


def scrape(max_comment_pages: int = None, max_review_pages: int = None):
    """
    爬取评论数据
    
    Args:
        max_comment_pages: 短评最大页数
        max_review_pages: 长评最大页数
    """
    print("\n🕷️ 启动爬虫模式...")
    print("=" * 50)
    
    scraper = DoubanScraper(headless=False)  # 首次建议显示浏览器
    
    try:
        # 爬取所有数据
        data = scraper.scrape_all(
            max_comment_pages=max_comment_pages,
            max_review_pages=max_review_pages
        )
        
        # 保存原始数据
        scraper.save_raw_data()
        
        print("\n✅ 爬取完成！")
        print(f"   短评: {len(data.get('comments', []))} 条")
        print(f"   长评: {len(data.get('reviews', []))} 条")
        
        return data
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，正在保存已爬取的数据...")
        scraper.save_raw_data()
        print("数据已保存。")
    except Exception as e:
        print(f"\n❌ 爬取出错: {e}")
        scraper.save_raw_data()
        raise
    finally:
        scraper.stop()


def analyze():
    """分析已爬取的数据"""
    print("\n📊 启动分析模式...")
    print("=" * 50)
    
    # 检查数据文件是否存在
    comments_file = os.path.join(DATA_DIR, 'comments.csv')
    reviews_file = os.path.join(DATA_DIR, 'reviews.csv')
    
    if not os.path.exists(comments_file):
        print(f"❌ 找不到数据文件: {comments_file}")
        print("请先运行爬虫: python main.py --scrape")
        return
    
    # 创建分类器并加载数据
    classifier = CommentClassifier()
    classifier.load_from_csv(comments_file, reviews_file)
    
    # 执行分类
    classifier.classify_all()
    
    # 生成统计
    classifier.generate_statistics()
    
    # 打印摘要
    classifier.print_summary()
    
    # 保存结果
    classifier.save_results()
    
    print("\n✅ 分析完成！")


def run_all(max_comment_pages: int = None, max_review_pages: int = None):
    """运行完整流程：爬取 + 分析"""
    print("\n🚀 启动完整流程...")
    
    # 爬取数据
    data = scrape(max_comment_pages, max_review_pages)
    
    if data and data.get('comments'):
        # 直接使用爬取的数据进行分析
        classifier = CommentClassifier(
            comments=data.get('comments', []),
            reviews=data.get('reviews', [])
        )
        
        # 执行分类
        classifier.classify_all()
        
        # 生成统计
        classifier.generate_statistics()
        
        # 打印摘要
        classifier.print_summary()
        
        # 保存结果
        classifier.save_results()
        
        print("\n✅ 完整流程执行完毕！")
    else:
        print("\n⚠️ 没有爬取到数据，跳过分析步骤。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='豆瓣电影评论爬虫 & 分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --login                    # 首次运行，手动登录
  python main.py --scrape                   # 爬取所有评论
  python main.py --scrape --pages 5         # 只爬取前5页短评
  python main.py --analyze                  # 分析已有数据
  python main.py --all                      # 爬取 + 分析
  python main.py --all --pages 10           # 爬取前10页 + 分析
        """
    )
    
    parser.add_argument('--login', action='store_true',
                        help='手动登录豆瓣账号（首次运行需要）')
    parser.add_argument('--scrape', action='store_true',
                        help='爬取评论数据')
    parser.add_argument('--analyze', action='store_true',
                        help='分析已爬取的数据')
    parser.add_argument('--all', action='store_true',
                        help='运行完整流程（爬取+分析）')
    parser.add_argument('--pages', type=int, default=None,
                        help='最大爬取页数（默认爬取全部）')
    parser.add_argument('--review-pages', type=int, default=None,
                        help='长评最大爬取页数（默认同--pages）')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print_banner()
    
    # 如果没有指定任何操作，显示帮助
    if not any([args.login, args.scrape, args.analyze, args.all]):
        parser.print_help()
        print("\n💡 快速开始:")
        print("   1. 首次运行: python main.py --login")
        print("   2. 爬取数据: python main.py --scrape")
        print("   3. 分析数据: python main.py --analyze")
        return
    
    # 执行对应操作
    if args.login:
        login()
    
    if args.scrape:
        review_pages = args.review_pages or args.pages
        scrape(max_comment_pages=args.pages, max_review_pages=review_pages)
    
    if args.analyze:
        analyze()
    
    if args.all:
        review_pages = args.review_pages or args.pages
        run_all(max_comment_pages=args.pages, max_review_pages=review_pages)


if __name__ == '__main__':
    main()
