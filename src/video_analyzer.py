"""
Video Analyzer using Google Gemini API
Sprint 2: E-Com Video Insider
"""

import os
import json
import time
import requests
import yt_dlp
from pathlib import Path
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

from .prompts import VIDEO_ANALYSIS_SYSTEM_PROMPT

# Load environment variables
load_dotenv()


class VideoAnalyzer:
    """
    视频内容分析器
    使用 Google Gemini 1.5 Pro API 分析短视频结构并生成翻拍建议
    """
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 Video Analyzer
        
        Args:
            api_key: Google Gemini API Key，如果不提供则从环境变量读取
            api_base: 自定义 API Base URL（用于 KIE API 等代理服务）
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.api_base = api_base or os.getenv('GEMINI_API_BASE')
        
        # 如果使用 KIE API，可能不需要单独的 API Key（认证信息包含在 URL 中）
        if not self.api_key and not self.api_base:
            raise ValueError("GEMINI_API_KEY 或 GEMINI_API_BASE 至少需要配置一个")
        
        # 如果没有 API Key 但有 API Base，使用一个默认值
        if not self.api_key and self.api_base:
            self.api_key = "dummy_key_for_kie_api"  # KIE API 可能不需要真实的 key
        
        # 配置 Gemini API
        if self.api_base:
            # 使用自定义 API Base URL（KIE API）
            genai.configure(
                api_key=self.api_key,
                transport='rest',
                client_options={'api_endpoint': self.api_base}
            )
            print(f"✅ 使用自定义 API Base: {self.api_base}")
        else:
            # 使用默认 Google API
            genai.configure(api_key=self.api_key)
            print("✅ 使用 Google 官方 API")
        
        # 使用 Gemini Flash Latest（支持长视频输入，更高的免费配额）
        # 注意: 移除 system_instruction 以兼容 Google AI Studio 的稳定版 API (v1)
        # Flash 版本比 Pro 版本更快，配额更高，质量足够好
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            generation_config={
                'temperature': 0.7,
            }
        )
        
        # 保存系统提示词，稍后与用户提示词组合使用
        self.system_prompt = VIDEO_ANALYSIS_SYSTEM_PROMPT
        
        # 临时文件夹
        self.temp_dir = Path('/home/ubuntu/ecom-video-insider/data/temp')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video_with_ytdlp(self, video_url: str) -> str:
        """
        使用 yt-dlp 从 TikTok/Instagram/YouTube 下载视频
        
        Args:
            video_url: TikTok/Instagram/YouTube 视频 URL
            
        Returns:
            本地视频文件路径
        """
        print(f"📥 使用 yt-dlp 下载视频: {video_url}")
        
        # 生成输出文件名
        timestamp = int(time.time())
        output_template = str(self.temp_dir / f"video_{timestamp}.%(ext)s")
        
        # yt-dlp 配置
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # 优先下载 mp4 格式
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 下载视频
                info = ydl.extract_info(video_url, download=True)
                
                # 获取实际下载的文件路径
                filename = ydl.prepare_filename(info)
                
                print(f"✅ 视频下载完成: {filename}")
                return filename
                
        except Exception as e:
            print(f"❌ yt-dlp 下载失败: {str(e)}")
            raise ValueError(f"视频下载失败: {str(e)}")
    
    def download_video(self, video_url: str, output_filename: Optional[str] = None) -> str:
        """
        下载视频到本地临时文件夹（兼容旧的直接下载链接方式）
        
        Args:
            video_url: 视频下载链接
            output_filename: 输出文件名（可选，默认自动生成）
            
        Returns:
            本地视频文件路径
        """
        print(f"📥 开始下载视频: {video_url}")
        
        if not output_filename:
            # 使用时间戳生成唯一文件名
            timestamp = int(time.time())
            output_filename = f"video_{timestamp}.mp4"
        
        output_path = self.temp_dir / output_filename
        
        try:
            # 下载视频
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 写入文件
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ 视频下载完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 视频下载失败: {str(e)}")
            raise
    
    def upload_to_gemini(self, video_path: str, max_wait_time: int = 300):
        """
        上传视频到 Gemini API 并等待处理完成
        
        Args:
            video_path: 本地视频文件路径
            max_wait_time: 最大等待时间（秒），默认 300 秒
            
        Returns:
            Gemini File 对象
        """
        print(f"☁️  开始上传视频到 Gemini API: {video_path}")
        
        try:
            # 上传文件
            video_file = genai.upload_file(path=video_path)
            print(f"✅ 视频上传成功，文件名: {video_file.name}")
            print(f"⏳ 等待 Gemini 处理视频...")
            
            # 关键：等待文件状态变为 ACTIVE
            start_time = time.time()
            while video_file.state.name == "PROCESSING":
                elapsed_time = time.time() - start_time
                
                if elapsed_time > max_wait_time:
                    raise TimeoutError(f"视频处理超时（超过 {max_wait_time} 秒）")
                
                print(f"  状态: {video_file.state.name}，已等待 {int(elapsed_time)} 秒...")
                time.sleep(5)  # 每 5 秒检查一次
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise ValueError(f"视频处理失败: {video_file.state.name}")
            
            print(f"✅ 视频处理完成，状态: {video_file.state.name}")
            return video_file
            
        except Exception as e:
            print(f"❌ 视频上传或处理失败: {str(e)}")
            raise
    
    def analyze_video_structure(self, video_url: str, cleanup: bool = True) -> Dict:
        """
        完整的视频分析流程
        
        Args:
            video_url: 视频下载链接（来自 Sprint 1 的 TikTokFetcher）
            cleanup: 是否在分析后删除临时文件，默认 True
            
        Returns:
            包含视频分析结果的字典，格式如下：
            {
                'video_metadata': {...},
                'structure_breakdown': {...},
                'creative_insight': {...},
                'lazada_adaptation_brief': {...}
            }
        """
        print("=" * 60)
        print("🎬 开始视频结构分析")
        print("=" * 60)
        
        local_video_path = None
        
        try:
            # 步骤 1: 下载视频
            local_video_path = self.download_video(video_url)
            
            # 步骤 2: 上传到 Gemini 并等待处理
            video_file = self.upload_to_gemini(local_video_path)
            
            # 步骤 3: 调用 Gemini API 进行分析
            print("🤖 开始 AI 分析...")
            
            # 组合系统提示词和用户提示词
            # 因为 Google AI Studio API (v1) 不支持 system_instruction
            combined_prompt = f"""{self.system_prompt}

---

Now, please analyze the following video according to the framework above.
Return your analysis in valid JSON format.
"""
            
            response = self.model.generate_content([video_file, combined_prompt])
            
            # 步骤 4: 解析 JSON 响应
            try:
                analysis_result = json.loads(response.text)
                print("✅ 分析完成！")
                
                # 打印关键信息
                self._print_analysis_summary(analysis_result)
                
                return analysis_result
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON 解析失败，返回原始文本")
                print(f"原始响应: {response.text}")
                raise ValueError(f"Gemini 返回的不是有效的 JSON: {e}")
            
        except Exception as e:
            print(f"❌ 视频分析失败: {str(e)}")
            raise
        
        finally:
            # 清理临时文件
            if cleanup and local_video_path and os.path.exists(local_video_path):
                try:
                    os.remove(local_video_path)
                    print(f"🧹 已清理临时文件: {local_video_path}")
                except Exception as e:
                    print(f"⚠️  清理临时文件失败: {e}")
    
    def _print_analysis_summary(self, analysis: Dict):
        """打印分析结果摘要"""
        print("\n" + "=" * 60)
        print("📊 分析结果摘要")
        print("=" * 60)
        
        # 视频元数据
        metadata = analysis.get('video_metadata', {})
        print(f"\n🎥 视频元数据:")
        print(f"  语言: {metadata.get('primary_language', 'N/A')}")
        print(f"  情感: {metadata.get('estimated_sentiment', 'N/A')}")
        
        # 结构拆解
        structure = analysis.get('structure_breakdown', {})
        print(f"\n🎯 结构拆解:")
        print(f"  Hook 类型: {structure.get('hook_type', 'N/A')}")
        print(f"  痛点: {structure.get('pain_point_addressed', 'N/A')}")
        print(f"  产品出现时间: {structure.get('product_reveal_timestamp', 'N/A')}")
        print(f"  核心卖点: {structure.get('key_selling_proposition', 'N/A')}")
        
        # 创意洞察
        insight = analysis.get('creative_insight', {})
        print(f"\n💡 创意洞察:")
        print(f"  视觉风格: {insight.get('visual_style', 'N/A')}")
        print(f"  为什么有效: {insight.get('why_it_works', 'N/A')[:80]}...")
        
        # Lazada 翻拍建议
        adaptation = analysis.get('lazada_adaptation_brief', {})
        print(f"\n🎬 Lazada 翻拍建议:")
        print(f"  翻拍难度: {adaptation.get('remake_difficulty', 'N/A')}")
        print(f"  本地化建议: {adaptation.get('localization_tip', 'N/A')[:80]}...")
        
        print("=" * 60 + "\n")


def main():
    """
    测试函数 - 使用 Mock Data 模拟流程
    """
    print("=" * 60)
    print("Video Analyzer - Sprint 2 测试")
    print("=" * 60)
    
    # Mock Data 模式测试
    print("\n📋 模式: Mock Data 测试")
    mock_analysis = {
        "video_metadata": {
            "primary_language": "English",
            "estimated_sentiment": "Positive"
        },
        "structure_breakdown": {
            "hook_type": "Visual Shock",
            "hook_description": "Split screen showing before/after transformation with dramatic zoom",
            "pain_point_addressed": "Dirty, stained surfaces that are hard to clean",
            "product_reveal_timestamp": "00:05",
            "key_selling_proposition": "Effortless cleaning in seconds"
        },
        "creative_insight": {
            "why_it_works": "Uses satisfying transformation visual that triggers dopamine response",
            "visual_style": "UGC with high production value"
        },
        "lazada_adaptation_brief": {
            "remake_difficulty": "Medium",
            "script_template": "1. Show dirty surface close-up 2. Apply product with satisfying sound 3. Reveal clean result 4. Show price and CTA",
            "localization_tip": "Emphasize cash-on-delivery option and add local language subtitles"
        }
    }
    
    print("\n✨ Mock 分析结果示例:")
    print(json.dumps(mock_analysis, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("💡 提示: 要测试真实 API，请:")
    print("  1. 确保 .env 中已配置 GEMINI_API_KEY")
    print("  2. 准备一个视频下载链接")
    print("  3. 取消下方代码注释并运行")
    print("=" * 60)
    
    # 真实 API 测试（默认注释）
    """
    # 取消注释以测试真实 API
    try:
        analyzer = VideoAnalyzer()
        
        # 使用 Sprint 1 获取的视频下载链接
        video_download_url = "https://example.com/video.mp4"  # 替换为真实 URL
        
        result = analyzer.analyze_video_structure(video_download_url)
        
        print("\n🎉 真实 API 测试结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    """


if __name__ == "__main__":
    main()
