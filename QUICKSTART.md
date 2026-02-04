# 快速开始指南

本指南帮助您在 5 分钟内快速启动 E-Com Video Insider 的数据管道功能。

## 🚀 三步快速启动

### 第一步: 配置环境

```bash
# 1. 进入项目目录
cd /home/ubuntu/ecom-video-insider

# 2. 创建环境配置文件
cp .env.example .env

# 3. 编辑 .env 文件，填入你的 Apify API Token
# APIFY_API_TOKEN=your_token_here
```

**获取 Apify API Token**: 访问 https://console.apify.com/ → Settings → Integrations → API Token

### 第二步: 安装依赖

```bash
sudo pip3 install -r requirements.txt
```

### 第三步: 测试运行

**选项 A: 使用模拟数据测试（无需 API Token）**

```bash
python3.11 src/tiktok_fetcher.py
```

**选项 B: 使用真实 API 测试（需要配置 API Token）**

```python
# 创建一个测试脚本 test.py
from src.tiktok_fetcher import TikTokFetcher

fetcher = TikTokFetcher()
video_url = "https://www.tiktok.com/@user/video/1234567890"  # 替换为真实 URL
result = fetcher.fetch_video_data(video_url)

print(f"视频下载链接: {result['download_url']}")
print(f"点赞数: {result['likes']}")
print(f"评论数: {result['comments']}")
```

然后运行：

```bash
python3.11 test.py
```

## 📝 使用示例

### 基础用法

```python
from src.tiktok_fetcher import TikTokFetcher

# 初始化
fetcher = TikTokFetcher()

# 获取视频数据
video_data = fetcher.fetch_video_data("https://www.tiktok.com/@user/video/xxx")

# 访问数据
print(f"下载链接: {video_data['download_url']}")
print(f"点赞数: {video_data['likes']}")
print(f"评论数: {video_data['comments']}")
print(f"播放数: {video_data['views']}")
print(f"描述: {video_data['description']}")
```

### 批量处理

```python
from src.tiktok_fetcher import TikTokFetcher

urls = [
    "https://www.tiktok.com/@user1/video/111",
    "https://www.tiktok.com/@user2/video/222",
    "https://www.tiktok.com/@user3/video/333",
]

fetcher = TikTokFetcher()
results = []

for url in urls:
    try:
        data = fetcher.fetch_video_data(url)
        results.append(data)
        print(f"✅ {url}")
    except Exception as e:
        print(f"❌ {url}: {e}")

print(f"\n成功获取 {len(results)} 个视频数据")
```

## 📊 返回数据格式

`fetch_video_data()` 方法返回一个包含以下字段的字典：

| 字段 | 类型 | 说明 |
|------|------|------|
| `video_url` | str | 原始视频 URL |
| `download_url` | str | 视频下载链接 |
| `likes` | int | 点赞数 |
| `comments` | int | 评论数 |
| `shares` | int | 分享数 |
| `views` | int | 播放数 |
| `publish_time` | str | 发布时间 (ISO 格式) |
| `description` | str | 视频描述文本 |
| `author` | str | 作者用户名 |
| `music` | str | 背景音乐名称 |
| `duration` | int | 视频时长（秒） |
| `hashtags` | list | 标签列表 |

## ⚠️ 注意事项

1. **API 配额**: Apify 免费账号有计算单元限制，请合理使用
2. **速率限制**: 避免短时间内发起大量请求
3. **视频可用性**: 某些视频可能因隐私设置或删除而无法获取
4. **数据时效性**: 互动数据（点赞、评论等）会随时间变化

## 🔧 故障排查

### 问题: 提示 "APIFY_API_TOKEN 未设置"

**解决**: 确保 `.env` 文件存在且包含有效的 `APIFY_API_TOKEN`

### 问题: Actor 运行失败

**可能原因**:
- API Token 无效
- 视频 URL 格式错误
- Apify 账号余额不足

**解决**: 检查 Apify Console 中的运行日志

### 问题: 返回数据为空

**可能原因**:
- 视频已被删除或设为私密
- 视频 URL 不正确

**解决**: 尝试使用其他公开视频进行测试

## 📚 更多资源

- [完整 README](./README.md)
- [详细配置指南](./SETUP_GUIDE.md)
- [使用示例代码](./example_usage.py)

## 🎯 下一步

Sprint 1 完成后，您可以：
1. 集成 Gemini API 进行视频内容分析（Sprint 2）
2. 构建 Streamlit UI 界面（Sprint 3）
3. 添加批量处理和数据导出功能（Sprint 4）
