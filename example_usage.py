"""
E-Com Video Insider - 使用示例
演示如何使用 TikTokFetcher 获取视频数据
"""

from src.tiktok_fetcher import TikTokFetcher


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)
    
    # 初始化 Fetcher（会自动从 .env 读取 API Token）
    fetcher = TikTokFetcher()
    
    # 替换为你要分析的 TikTok 视频 URL
    video_url = "https://www.tiktok.com/@user/video/1234567890"
    
    try:
        # 获取视频数据
        video_data = fetcher.fetch_video_data(video_url)
        
        # 打印关键信息
        print(f"\n📹 视频信息:")
        print(f"  作者: {video_data['author']}")
        print(f"  描述: {video_data['description']}")
        print(f"  时长: {video_data['duration']} 秒")
        print(f"\n📊 互动数据:")
        print(f"  👁️  播放: {video_data['views']:,}")
        print(f"  ❤️  点赞: {video_data['likes']:,}")
        print(f"  💬 评论: {video_data['comments']:,}")
        print(f"  🔄 分享: {video_data['shares']:,}")
        print(f"\n⬇️  下载链接:")
        print(f"  {video_data['download_url']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def example_batch_processing():
    """批量处理示例（未来功能预览）"""
    print("\n" + "=" * 60)
    print("示例 2: 批量处理（未来功能）")
    print("=" * 60)
    
    video_urls = [
        "https://www.tiktok.com/@user1/video/111",
        "https://www.tiktok.com/@user2/video/222",
        "https://www.tiktok.com/@user3/video/333",
    ]
    
    fetcher = TikTokFetcher()
    results = []
    
    for url in video_urls:
        try:
            data = fetcher.fetch_video_data(url)
            results.append(data)
            print(f"✅ 成功: {url}")
        except Exception as e:
            print(f"❌ 失败: {url} - {e}")
    
    print(f"\n📦 共获取 {len(results)} 个视频数据")


if __name__ == "__main__":
    print("🚀 E-Com Video Insider - Sprint 1 示例\n")
    
    # 运行基础示例
    example_basic_usage()
    
    # 取消注释以测试批量处理
    # example_batch_processing()
