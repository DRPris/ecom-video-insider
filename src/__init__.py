"""
E-Com Video Insider
A tool for analyzing TikTok/Reels videos and generating Lazada ad scripts
"""

from .tiktok_fetcher import TikTokFetcher
from .video_analyzer import VideoAnalyzer
from .prompts import VIDEO_ANALYSIS_SYSTEM_PROMPT

__version__ = "0.2.0"
__all__ = ['TikTokFetcher', 'VideoAnalyzer', 'VIDEO_ANALYSIS_SYSTEM_PROMPT']
