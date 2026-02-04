# yt-dlp 集成说明

本文档说明 E-Com Video Insider 如何集成 yt-dlp 用于视频下载。

## 架构变更

### 之前的架构（Sprint 1-2）

```
用户输入 TikTok URL
    ↓
Apify 获取视频数据（包括 download_url）
    ↓
使用 requests 下载视频
    ↓
上传到 Gemini 分析
```

**问题**: 许多 Apify Actor 不提供 `download_url`，导致无法下载视频。

### 当前架构（Sprint 3 最终版）

```
用户输入 TikTok URL
    ↓
Apify 获取元数据（点赞、评论、播放量等）
    ↓
yt-dlp 直接从 TikTok URL 下载视频
    ↓
上传到 Gemini 分析
    ↓
返回结果（元数据 + AI 分析）
```

**优势**:
- ✅ 不依赖 Apify 的 download_url
- ✅ 支持多平台（TikTok、Instagram、YouTube）
- ✅ 更可靠、更快速
- ✅ 完全免费开源

## 技术实现

### 1. 安装 yt-dlp

```bash
sudo pip3 install yt-dlp
```

已添加到 `requirements.txt`：
```
yt-dlp==2026.2.4
```

### 2. 新增方法：`download_video_with_ytdlp()`

在 `src/video_analyzer.py` 中新增：

```python
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
```

### 3. 更新 app.py 流程

修改前：
```python
# 使用 Apify 返回的 download_url
analysis_result = analyzer.analyze_video_structure(video_data['download_url'])
```

修改后：
```python
# 使用 yt-dlp 下载视频（使用原始 TikTok URL）
video_path = analyzer.download_video_with_ytdlp(video_url)

# 上传到 Gemini 并分析
video_file = analyzer.upload_to_gemini(video_path)
analysis_result = analyzer.analyze_with_gemini(video_file)

# 清理临时文件
analyzer.cleanup_temp_file(video_path)
```

## yt-dlp 配置说明

### 关键配置项

```python
ydl_opts = {
    'format': 'best[ext=mp4]/best',  # 优先下载 mp4 格式
    'outtmpl': output_template,       # 输出文件路径模板
    'quiet': False,                   # 显示下载进度
    'no_warnings': False,             # 显示警告信息
    'extract_flat': False,            # 完整提取视频信息
    'nocheckcertificate': True,       # 忽略 SSL 证书验证
}
```

### 支持的平台

yt-dlp 支持 1000+ 网站，包括：

- **短视频平台**
  - TikTok
  - Instagram Reels
  - YouTube Shorts
  - Facebook Reels
  - Snapchat Spotlight

- **长视频平台**
  - YouTube
  - Vimeo
  - Dailymotion

- **其他平台**
  - Twitter/X
  - Reddit
  - Bilibili

### 格式选择策略

```python
'format': 'best[ext=mp4]/best'
```

这个配置的含义：
1. 优先选择 mp4 格式的最佳质量视频
2. 如果没有 mp4，则选择其他格式的最佳质量视频
3. yt-dlp 会自动处理格式转换

## 性能优化

### 1. 视频大小限制

建议在生产环境中添加文件大小限制：

```python
ydl_opts = {
    'format': 'best[ext=mp4][filesize<100M]/best[filesize<100M]/best',
    # ...
}
```

### 2. 下载超时

```python
ydl_opts = {
    'socket_timeout': 30,  # 30 秒超时
    # ...
}
```

### 3. 代理配置

如果需要使用代理：

```python
ydl_opts = {
    'proxy': 'http://proxy.example.com:8080',
    # ...
}
```

## 错误处理

### 常见错误

1. **视频不可用**
   ```
   ERROR: Video unavailable
   ```
   - 原因：视频已被删除或设为私密
   - 解决：提示用户检查 URL

2. **地区限制**
   ```
   ERROR: This video is not available in your country
   ```
   - 原因：视频有地区限制
   - 解决：使用 VPN 或代理

3. **下载失败**
   ```
   ERROR: Unable to download webpage
   ```
   - 原因：网络问题或平台反爬虫
   - 解决：重试或更新 yt-dlp

### 错误处理代码

```python
try:
    video_path = analyzer.download_video_with_ytdlp(video_url)
except ValueError as e:
    st.error(f"❌ 视频下载失败: {str(e)}")
    st.info("💡 建议：检查视频 URL 是否正确，或视频是否可公开访问")
    st.stop()
```

## 与 Apify 的协作

### Apify 的作用

- ✅ 获取视频元数据（点赞、评论、播放量）
- ✅ 批量爬取视频列表
- ✅ 获取作者信息
- ✅ 获取标签和描述

### yt-dlp 的作用

- ✅ 下载视频文件
- ✅ 支持多平台
- ✅ 自动处理格式转换
- ✅ 免费且可靠

### 最佳实践

```python
# 1. 使用 Apify 获取元数据
fetcher = TikTokFetcher(api_token=apify_token)
video_data = fetcher.fetch_video_data(video_url)

# 2. 使用 yt-dlp 下载视频
analyzer = VideoAnalyzer(api_key=gemini_key)
video_path = analyzer.download_video_with_ytdlp(video_url)

# 3. 结合两者的数据
result = {
    'metadata': video_data,  # 来自 Apify
    'analysis': analysis_result,  # 来自 Gemini
}
```

## 生产环境部署建议

### 1. 异步任务队列

使用 Celery 或 Redis Queue 处理视频下载：

```python
@celery.task
def download_and_analyze(video_url):
    video_path = download_video_with_ytdlp(video_url)
    result = analyze_video(video_path)
    return result
```

### 2. 视频缓存

避免重复下载相同视频：

```python
import hashlib

def get_video_cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()

def download_with_cache(url):
    cache_key = get_video_cache_key(url)
    cached_path = f"/cache/{cache_key}.mp4"
    
    if os.path.exists(cached_path):
        return cached_path
    
    # 下载并缓存
    video_path = download_video_with_ytdlp(url)
    shutil.copy(video_path, cached_path)
    return cached_path
```

### 3. 存储优化

使用对象存储（如 AWS S3）存储视频：

```python
def upload_to_s3(video_path):
    s3_client.upload_file(video_path, bucket_name, object_key)
    return s3_url
```

### 4. 监控和日志

```python
import logging

logging.info(f"开始下载视频: {video_url}")
logging.info(f"视频大小: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
logging.info(f"下载耗时: {elapsed_time:.2f} 秒")
```

## 更新和维护

### 更新 yt-dlp

```bash
sudo pip3 install --upgrade yt-dlp
```

### 检查版本

```bash
yt-dlp --version
```

### 测试下载

```bash
yt-dlp "https://www.tiktok.com/@user/video/123" -o "test.mp4"
```

## 总结

通过集成 yt-dlp，E-Com Video Insider 现在拥有：

1. **更强的可靠性** - 不依赖 Apify 的 download_url
2. **更好的扩展性** - 支持多个视频平台
3. **更低的成本** - yt-dlp 完全免费
4. **更快的速度** - 直接下载，无需中间环节

这是一个面向生产环境的最佳实践架构！🚀
