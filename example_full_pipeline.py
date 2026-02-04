"""
E-Com Video Insider - 完整流程示例
Sprint 1 + Sprint 2: 从 TikTok URL 到视频分析结果
"""

import json
from src.tiktok_fetcher import TikTokFetcher
from src.video_analyzer import VideoAnalyzer


def full_pipeline_example(tiktok_url: str):
    """
    完整的数据管道示例：
    1. 使用 TikTokFetcher 获取视频元数据和下载链接
    2. 使用 VideoAnalyzer 分析视频结构
    3. 输出完整的分析报告
    
    Args:
        tiktok_url: TikTok 视频 URL
    """
    print("=" * 80)
    print("🚀 E-Com Video Insider - 完整流程")
    print("=" * 80)
    
    try:
        # ========== Sprint 1: 获取视频数据 ==========
        print("\n📍 阶段 1: 获取 TikTok 视频数据")
        print("-" * 80)
        
        fetcher = TikTokFetcher()
        video_data = fetcher.fetch_video_data(tiktok_url)
        
        print(f"\n✅ 视频数据获取成功:")
        print(f"  作者: {video_data['author']}")
        print(f"  描述: {video_data['description'][:50]}...")
        print(f"  播放: {video_data['views']:,} | 点赞: {video_data['likes']:,}")
        print(f"  下载链接: {video_data['download_url'][:60]}...")
        
        # ========== Sprint 2: 分析视频结构 ==========
        print("\n📍 阶段 2: AI 视频结构分析")
        print("-" * 80)
        
        analyzer = VideoAnalyzer()
        analysis_result = analyzer.analyze_video_structure(video_data['download_url'])
        
        # ========== 生成综合报告 ==========
        print("\n📍 阶段 3: 生成综合报告")
        print("-" * 80)
        
        report = {
            "source_video": {
                "url": tiktok_url,
                "author": video_data['author'],
                "description": video_data['description'],
                "engagement": {
                    "views": video_data['views'],
                    "likes": video_data['likes'],
                    "comments": video_data['comments'],
                    "shares": video_data['shares']
                }
            },
            "ai_analysis": analysis_result
        }
        
        # 保存报告
        output_file = "/home/ubuntu/ecom-video-insider/data/analysis_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 完整报告已保存: {output_file}")
        
        # 打印关键洞察
        print("\n" + "=" * 80)
        print("🎯 关键洞察总结")
        print("=" * 80)
        
        structure = analysis_result.get('structure_breakdown', {})
        adaptation = analysis_result.get('lazada_adaptation_brief', {})
        
        print(f"\n📊 原视频表现:")
        print(f"  播放量: {video_data['views']:,}")
        print(f"  互动率: {((video_data['likes'] + video_data['comments']) / video_data['views'] * 100):.2f}%")
        
        print(f"\n🎬 视频结构:")
        print(f"  Hook 策略: {structure.get('hook_type', 'N/A')}")
        print(f"  核心卖点: {structure.get('key_selling_proposition', 'N/A')}")
        print(f"  产品出现: {structure.get('product_reveal_timestamp', 'N/A')}")
        
        print(f"\n🔄 Lazada 翻拍建议:")
        print(f"  难度评估: {adaptation.get('remake_difficulty', 'N/A')}")
        print(f"  脚本模板: {adaptation.get('script_template', 'N/A')[:100]}...")
        print(f"  本地化建议: {adaptation.get('localization_tip', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("✅ 流程完成！")
        print("=" * 80)
        
        return report
        
    except Exception as e:
        print(f"\n❌ 流程失败: {str(e)}")
        raise


def mock_pipeline_demo():
    """
    使用 Mock Data 演示完整流程（无需 API）
    """
    print("=" * 80)
    print("📋 Mock Data 演示 - 完整流程")
    print("=" * 80)
    
    # Mock Sprint 1 数据
    mock_video_data = {
        'author': 'viral_seller_123',
        'description': '🔥 This cleaning hack will change your life! #lazada #cleaning',
        'views': 1250000,
        'likes': 85000,
        'comments': 3200,
        'shares': 12000,
        'download_url': 'https://example.com/mock_video.mp4'
    }
    
    # Mock Sprint 2 分析结果
    mock_analysis = {
        "video_metadata": {
            "primary_language": "English",
            "estimated_sentiment": "Positive"
        },
        "structure_breakdown": {
            "hook_type": "Visual Shock + Verbal Question",
            "hook_description": "Opens with messy kitchen and voice asking 'Tired of scrubbing for hours?'",
            "pain_point_addressed": "Time-consuming cleaning with poor results",
            "product_reveal_timestamp": "00:04",
            "key_selling_proposition": "Cleans in 30 seconds without scrubbing"
        },
        "creative_insight": {
            "why_it_works": "Combines relatable pain point with instant gratification visual proof",
            "visual_style": "UGC with authentic home setting"
        },
        "lazada_adaptation_brief": {
            "remake_difficulty": "Low",
            "script_template": "1. Show dirty surface (2s) 2. Ask problem question (2s) 3. Apply product with timer overlay (5s) 4. Reveal result + price (3s) 5. CTA: 'Order now on Lazada' (2s)",
            "localization_tip": "Add Bahasa/Thai subtitles, emphasize free shipping and COD, show Lazada app interface at end"
        }
    }
    
    # 生成综合报告
    report = {
        "source_video": {
            "url": "https://www.tiktok.com/@viral_seller_123/video/mock123",
            "author": mock_video_data['author'],
            "description": mock_video_data['description'],
            "engagement": {
                "views": mock_video_data['views'],
                "likes": mock_video_data['likes'],
                "comments": mock_video_data['comments'],
                "shares": mock_video_data['shares']
            }
        },
        "ai_analysis": mock_analysis
    }
    
    print("\n✨ Mock 综合报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("💡 这就是真实 API 调用后的完整输出格式")
    print("=" * 80)


if __name__ == "__main__":
    # 运行 Mock 演示
    mock_pipeline_demo()
    
    print("\n\n")
    print("=" * 80)
    print("🔧 要测试真实 API，请:")
    print("  1. 确保 .env 中配置了 APIFY_API_TOKEN 和 GEMINI_API_KEY")
    print("  2. 取消下方注释并替换为真实 TikTok URL")
    print("=" * 80)
    
    # 真实 API 测试（默认注释）
    """
    # 取消注释以测试真实 API
    test_url = "https://www.tiktok.com/@user/video/1234567890"  # 替换为真实 URL
    result = full_pipeline_example(test_url)
    """
