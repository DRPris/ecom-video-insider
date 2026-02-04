# 故障排查指南

本文档帮助你解决使用 E-Com Video Insider 时可能遇到的常见问题。

## 错误 1: "Invalid URL '': No scheme supplied"

### 症状
```
MissingSchema: Invalid URL '': No scheme supplied. Perhaps you meant https://?
```

### 原因
Apify 返回的视频数据中没有包含有效的 `download_url` 字段，导致视频下载失败。

### 可能的原因

1. **TikTok URL 格式不正确**
   - 确保 URL 是完整的 TikTok 视频链接
   - 正确格式：`https://www.tiktok.com/@username/video/1234567890`
   - 错误格式：`tiktok.com/video/123` 或 `@username/video/123`

2. **Apify Actor 版本或配置问题**
   - 不同的 Apify TikTok Scraper Actor 返回的数据结构可能不同
   - 某些 Actor 可能不支持下载链接提取

3. **TikTok 视频不可用**
   - 视频已被删除
   - 视频设置为私密
   - 地区限制导致无法访问

### 解决方案

#### 方案 1: 检查 Apify 返回的原始数据

应用现在会在遇到此错误时自动显示 Apify 返回的原始数据。查看 `raw_data` 字段，找到可用的视频 URL 字段名。

#### 方案 2: 更换 Apify Actor

如果当前使用的 Actor 不支持视频下载，可以尝试其他 TikTok Scraper Actor：

推荐的 Apify Actors：
- `clockworks/tiktok-scraper`
- `apify/tiktok-scraper`
- `curious_coder/tiktok-scraper`

修改 `src/tiktok_fetcher.py` 中的 `actor_id`：

```python
self.actor_id = "your_chosen_actor_id"
```

#### 方案 3: 手动指定视频 URL

如果你已经有视频的直接下载链接，可以修改代码跳过 Apify 步骤：

1. 在 `app.py` 中添加一个额外的输入框用于直接输入视频下载 URL
2. 如果提供了直接 URL，跳过 Apify 调用

### 调试步骤

1. **查看 Apify 返回的原始数据**
   ```python
   # 在 example_usage.py 中运行
   video_data = fetcher.fetch_video_data(video_url)
   print(json.dumps(video_data['raw_data'], indent=2))
   ```

2. **检查可用的 URL 字段**
   
   常见的字段名：
   - `videoUrl`
   - `downloadAddr`
   - `video.downloadAddr`
   - `video.playAddr`
   - `playAddr`

3. **更新字段映射**
   
   在 `src/tiktok_fetcher.py` 的 `_format_video_data` 方法中添加新的字段映射：
   
   ```python
   download_url = (
       raw_data.get('videoUrl') or 
       raw_data.get('downloadAddr') or 
       raw_data.get('video', {}).get('downloadAddr') or
       raw_data.get('video', {}).get('playAddr') or
       raw_data.get('your_new_field_name') or  # 添加新字段
       ''
   )
   ```

## 错误 2: "请至少配置 Gemini API Key 或 API Base URL 之一"

### 症状
点击"Analyze Now"按钮后，提示需要配置 API。

### 解决方案
在侧边栏至少填写以下之一：
- **Gemini API Key**: 如果使用 Google 官方 API
- **Gemini API Base URL**: 如果使用 KIE API 或其他代理服务

## 错误 3: Gemini API 调用失败

### 可能的原因

1. **API Key 无效**
   - 检查 API Key 是否正确
   - 确认 API Key 未过期

2. **API Base URL 配置错误**
   - 确保 URL 格式正确（包含 `https://`）
   - 确认端点可访问

3. **视频文件过大**
   - Gemini API 对文件大小有限制
   - 建议使用 2 分钟以内的视频

### 解决方案

1. **验证 API 配置**
   ```bash
   # 测试 Google 官方 API
   curl -H "Content-Type: application/json" \
        -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_API_KEY"
   ```

2. **检查视频大小**
   ```bash
   # 下载视频并检查大小
   curl -I "VIDEO_DOWNLOAD_URL"
   ```

## 错误 4: Apify API 调用失败

### 可能的原因

1. **API Token 无效**
2. **API 配额用尽**
3. **Actor 不存在或无权访问**

### 解决方案

1. **验证 Apify Token**
   - 登录 https://console.apify.com/
   - 检查 Token 是否有效
   - 查看剩余配额

2. **检查 Actor 可用性**
   ```bash
   curl "https://api.apify.com/v2/acts/YOUR_ACTOR_ID" \
        -H "Authorization: Bearer YOUR_API_TOKEN"
   ```

## 常见问题

### Q: 为什么分析速度很慢？

**A**: 视频分析包含以下步骤：
1. 从 Apify 获取视频数据（5-10 秒）
2. 下载视频文件（取决于视频大小和网络速度）
3. 上传到 Gemini API（10-20 秒）
4. 等待 Gemini 处理视频（20-40 秒）
5. AI 分析并生成报告（10-20 秒）

总计约 1-2 分钟。

### Q: 可以批量分析视频吗？

**A**: 当前版本不支持批量分析。这是 Sprint 4 的计划功能。

### Q: 支持哪些平台的视频？

**A**: 当前版本仅支持 TikTok。未来版本将支持：
- Instagram Reels
- YouTube Shorts
- Facebook Reels

### Q: 分析结果保存在哪里？

**A**: 分析结果保存在 Streamlit 的 Session State 中，关闭浏览器后会丢失。你可以使用"Download JSON"或"Download Script"按钮导出结果。

## 获取帮助

如果以上方法都无法解决你的问题，请：

1. 查看应用的错误消息和 Traceback
2. 检查 Apify 返回的原始数据（应用会自动显示）
3. 在 GitHub Issues 中提交问题（如果项目开源）
4. 联系开发者并提供详细的错误信息

## 调试模式

如果需要更详细的调试信息，可以在命令行运行应用：

```bash
cd /home/ubuntu/ecom-video-insider
streamlit run app.py
```

这样可以在终端中看到完整的日志输出。
