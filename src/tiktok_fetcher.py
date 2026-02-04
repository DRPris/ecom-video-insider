"""
TikTok Video Data Fetcher using Apify API
Sprint 1: Data Pipeline for E-Com Video Insider
"""

import os
import time
from typing import Dict, Optional
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TikTokFetcher:
    """
    TikTok 视频数据获取器
    使用 Apify 的 TikTok Scraper Actor 来获取视频元数据和下载链接
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        初始化 TikTok Fetcher
        
        Args:
            api_token: Apify API Token，如果不提供则从环境变量读取
        """
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN 未设置！请在 .env 文件中配置或作为参数传入")
        
        self.client = ApifyClient(self.api_token)
        
        # 使用 clockworks/tiktok-scraper Actor
        # 这是一个流行的 TikTok 数据抓取 Actor
        self.actor_id = "clockworks/tiktok-scraper"
    
    def fetch_video_data(self, video_url: str, max_wait_time: int = 120) -> Dict:
        """
        获取 TikTok 视频数据
        
        Args:
            video_url: TikTok 视频 URL (例如: https://www.tiktok.com/@user/video/1234567890)
            max_wait_time: 最大等待时间（秒），默认 120 秒
            
        Returns:
            包含视频数据的字典，格式如下：
            {
                'video_url': str,           # 原始视频 URL
                'download_url': str,        # 视频下载链接
                'likes': int,               # 点赞数
                'comments': int,            # 评论数
                'shares': int,              # 分享数
                'views': int,               # 播放数
                'publish_time': str,        # 发布时间
                'description': str,         # 视频描述
                'author': str,              # 作者用户名
                'music': str,               # 背景音乐
                'duration': int,            # 视频时长（秒）
            }
        """
        print(f"🚀 开始获取 TikTok 视频数据: {video_url}")
        
        # 配置 Actor 运行参数
        run_input = {
            "postURLs": [video_url],
            "resultsPerPage": 1,
            # 确保获取视频下载链接
            "shouldDownloadVideos": False,  # 我们只需要 URL，不需要 Apify 下载
            "shouldDownloadCovers": False,
            "shouldDownloadSubtitles": False,
        }
        
        try:
            # 运行 Actor
            print("⏳ 正在调用 Apify Actor...")
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # 等待运行完成并获取结果
            print("📥 正在获取数据...")
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
            
            if not dataset_items:
                raise ValueError("未能从 Apify 获取到视频数据，请检查视频 URL 是否正确")
            
            # 提取第一个结果
            video_data = dataset_items[0]
            
            # 格式化返回数据
            result = self._format_video_data(video_data)
            
            print("✅ 数据获取成功！")
            return result
            
        except Exception as e:
            print(f"❌ 获取视频数据失败: {str(e)}")
            raise
    
    def _format_video_data(self, raw_data: Dict) -> Dict:
        """
        格式化 Apify 返回的原始数据
        
        Args:
            raw_data: Apify Actor 返回的原始数据
            
        Returns:
            格式化后的视频数据字典
        """
        # Apify TikTok Scraper 的数据结构可能因 Actor 版本而异
        # 这里提供一个通用的映射逻辑
        
        # 尝试多个可能的字段名来获取下载链接
        download_url = (
            raw_data.get('videoUrl') or 
            raw_data.get('downloadAddr') or 
            raw_data.get('video', {}).get('downloadAddr') or
            raw_data.get('video', {}).get('playAddr') or
            ''
        )
        
        return {
            'video_url': raw_data.get('webVideoUrl', raw_data.get('videoUrl', '')),
            'download_url': download_url,
            'likes': raw_data.get('diggCount', 0),
            'comments': raw_data.get('commentCount', 0),
            'shares': raw_data.get('shareCount', 0),
            'views': raw_data.get('playCount', 0),
            'publish_time': raw_data.get('createTime', raw_data.get('createTimeISO', '')),
            'description': raw_data.get('text', raw_data.get('desc', '')),
            'author': raw_data.get('authorMeta', {}).get('name', raw_data.get('author', '')),
            'music': raw_data.get('musicMeta', {}).get('musicName', ''),
            'duration': raw_data.get('videoMeta', {}).get('duration', 0),
            'hashtags': raw_data.get('hashtags', []),
            'raw_data': raw_data  # 保留原始数据以便调试
        }


def main():
    """
    测试函数 - 使用 Mock Data 模拟流程
    """
    print("=" * 60)
    print("TikTok Video Fetcher - Sprint 1 测试")
    print("=" * 60)
    
    # Mock Data 模式测试
    print("\n📋 模式: Mock Data 测试")
    mock_data = {
        'video_url': 'https://www.tiktok.com/@example/video/1234567890',
        'download_url': 'https://example.com/video.mp4',
        'likes': 12500,
        'comments': 340,
        'shares': 890,
        'views': 156000,
        'publish_time': '2024-01-15T10:30:00Z',
        'description': '🔥 Amazing product review! #lazada #shopping',
        'author': 'example_user',
        'music': 'Trending Sound 2024',
        'duration': 45,
        'hashtags': ['lazada', 'shopping', 'review']
    }
    
    print("\n✨ Mock 数据示例:")
    for key, value in mock_data.items():
        if key != 'raw_data':
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("💡 提示: 要测试真实 API，请:")
    print("  1. 复制 .env.example 为 .env")
    print("  2. 在 .env 中填入你的 APIFY_API_TOKEN")
    print("  3. 取消下方代码注释并运行")
    print("=" * 60)
    
    # 真实 API 测试（默认注释）
    """
    # 取消注释以测试真实 API
    try:
        fetcher = TikTokFetcher()
        test_url = "https://www.tiktok.com/@example/video/1234567890"  # 替换为真实 URL
        result = fetcher.fetch_video_data(test_url)
        
        print("\n🎉 真实 API 测试结果:")
        for key, value in result.items():
            if key != 'raw_data':
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    """


if __name__ == "__main__":
    main()
