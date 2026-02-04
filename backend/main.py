"""
E-Com Video Insider - 后端 API
使用 FastAPI 封装第三方 API 调用，保护 API Keys
"""

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
import sys
from typing import Optional
from datetime import datetime
import json

# 添加父目录到路径以导入 src 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tiktok_fetcher import TikTokFetcher
from src.video_analyzer import VideoAnalyzer

# ---------------------------------------------------------
# 1. FastAPI 应用初始化
# ---------------------------------------------------------
app = FastAPI(
    title="E-Com Video Insider API",
    description="安全的视频分析 API，保护第三方 API Keys",
    version="1.0.0"
)

# 允许跨域请求（Streamlit 前端需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 2. 从环境变量加载 API Keys（安全）
# ---------------------------------------------------------
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "")

if not APIFY_API_TOKEN or not GEMINI_API_KEY:
    raise ValueError("必须设置 APIFY_API_TOKEN 和 GEMINI_API_KEY 环境变量")

# ---------------------------------------------------------
# 3. 用户认证与配额管理
# ---------------------------------------------------------

# 简单的用户数据库（生产环境应该使用真实数据库）
API_USERS = {
    "demo_token_123": {
        "username": "demo_user",
        "email": "demo@example.com",
        "quota_monthly": 100,
        "quota_used": 0,
        "rate_limit_per_minute": 10
    },
    "premium_token_456": {
        "username": "premium_user",
        "email": "premium@example.com",
        "quota_monthly": 1000,
        "quota_used": 0,
        "rate_limit_per_minute": 30
    }
}

def get_current_user(authorization: Optional[str] = Header(None)):
    """
    验证用户的 API Token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization header")
    
    # 支持 "Bearer token" 格式
    token = authorization.replace("Bearer ", "")
    
    if token not in API_USERS:
        raise HTTPException(status_code=401, detail="无效的 API Token")
    
    user = API_USERS[token]
    
    # 检查配额
    if user["quota_used"] >= user["quota_monthly"]:
        raise HTTPException(
            status_code=429, 
            detail=f"已达到月度配额限制 ({user['quota_monthly']} 次)"
        )
    
    return user

# ---------------------------------------------------------
# 4. API 数据模型
# ---------------------------------------------------------

class AnalyzeRequest(BaseModel):
    video_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://www.tiktok.com/@5.minute.recipes/video/7588608011745250591"
            }
        }

class AnalyzeResponse(BaseModel):
    success: bool
    metadata: dict
    analysis: dict
    timestamp: str
    quota_remaining: int

# ---------------------------------------------------------
# 5. API 端点
# ---------------------------------------------------------

@app.get("/")
def root():
    """
    API 根路径，返回基本信息
    """
    return {
        "service": "E-Com Video Insider API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health",
            "user_info": "/api/user"
        }
    }

@app.get("/health")
def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "apify_configured": bool(APIFY_API_TOKEN),
        "gemini_configured": bool(GEMINI_API_KEY)
    }

@app.get("/api/user")
def get_user_info(user: dict = Depends(get_current_user)):
    """
    获取当前用户信息和配额使用情况
    """
    return {
        "username": user["username"],
        "email": user["email"],
        "quota_monthly": user["quota_monthly"],
        "quota_used": user["quota_used"],
        "quota_remaining": user["quota_monthly"] - user["quota_used"],
        "rate_limit_per_minute": user["rate_limit_per_minute"]
    }

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_video(
    request: AnalyzeRequest,
    user: dict = Depends(get_current_user)
):
    """
    分析 TikTok/Instagram/YouTube Shorts 视频
    
    需要在 Authorization header 中提供有效的 API Token
    """
    try:
        print(f"📊 用户 {user['username']} 请求分析视频: {request.video_url}")
        
        # 1. 获取视频元数据（使用 Apify）
        print("📥 Step 1: 获取视频元数据...")
        fetcher = TikTokFetcher(api_token=APIFY_API_TOKEN)
        video_data = fetcher.fetch_video_data(str(request.video_url))
        
        # 2. 下载视频并分析（使用 Gemini）
        print("🤖 Step 2: 下载视频并分析...")
        analyzer = VideoAnalyzer(
            api_key=GEMINI_API_KEY,
            api_base=GEMINI_API_BASE if GEMINI_API_BASE else None
        )
        
        # 使用 yt-dlp 下载视频
        video_path = analyzer.download_video_with_ytdlp(str(request.video_url))
        
        # 上传到 Gemini 并分析
        video_file = analyzer.upload_to_gemini(video_path)
        prompt = "Please analyze this video according to the framework provided in your system instructions."
        response = analyzer.model.generate_content([video_file, prompt])
        
        # 解析 JSON 响应
        analysis_result = json.loads(response.text)
        
        # 清理临时文件
        analyzer.cleanup_temp_file(video_path)
        
        # 3. 更新用户配额
        user["quota_used"] += 1
        quota_remaining = user["quota_monthly"] - user["quota_used"]
        
        print(f"✅ 分析完成！剩余配额: {quota_remaining}")
        
        return AnalyzeResponse(
            success=True,
            metadata=video_data,
            analysis=analysis_result,
            timestamp=datetime.now().isoformat(),
            quota_remaining=quota_remaining
        )
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

# ---------------------------------------------------------
# 6. 启动说明
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 E-Com Video Insider Backend API")
    print("=" * 60)
    print(f"APIFY_API_TOKEN: {'✅ 已配置' if APIFY_API_TOKEN else '❌ 未配置'}")
    print(f"GEMINI_API_KEY: {'✅ 已配置' if GEMINI_API_KEY else '❌ 未配置'}")
    print("=" * 60)
    print("启动服务器...")
    print("API 文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
