# Google AI Studio API 使用指南

本文档说明如何使用从 Google AI Studio 获取的 API Key。

## 1. 获取 API Key

### 步骤 1: 访问 Google AI Studio

访问 https://aistudio.google.com/app/apikey

### 步骤 2: 创建 API Key

1. 点击 **"Create API Key"**
2. 选择一个 Google Cloud 项目（或创建新项目）
3. 复制生成的 API Key（格式：`AIzaSy...`）

## 2. API 版本说明

Google 提供两种 Gemini API：

| API 类型 | 端点 | 模型名称 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **Google AI Studio API** | `generativelanguage.googleapis.com` | `gemini-1.5-pro-latest` | 个人开发、快速原型 |
| **Vertex AI API** | `{region}-aiplatform.googleapis.com` | `gemini-1.5-pro` | 企业生产环境 |

**本项目使用 Google AI Studio API**。

## 3. 模型名称

### 可用的模型名称

从 Google AI Studio 获取的 API Key 支持以下模型名称：

```python
# ✅ 推荐：使用 latest 版本
model_name = 'gemini-1.5-pro-latest'

# ✅ 也可以使用具体版本
model_name = 'gemini-1.5-pro-001'

# ❌ 错误：不要使用 beta 版本的名称
model_name = 'gemini-1.5-pro'  # 这是 Vertex AI 的命名方式
```

### 为什么会出现 404 错误？

如果你看到错误：
```
404 models/gemini-1.5-pro is not found for API version v1beta
```

这是因为代码中使用了错误的模型名称。Google AI Studio API 使用**稳定版 (v1)** API，而不是 beta 版本。

## 4. 代码修复

### 修改前（错误）

```python
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',  # ❌ 错误
    ...
)
```

### 修改后（正确）

```python
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',  # ✅ 正确
    ...
)
```

## 5. 完整配置示例

### 配置 .env 文件

```dotenv
# Apify API Token
APIFY_API_TOKEN=apify_api_xxxxxxxxx

# Google AI Studio API Key
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 不需要填写 API Base URL（使用默认的 Google 端点）
GEMINI_API_BASE=
```

### Python 代码

```python
import google.generativeai as genai
import os

# 配置 API Key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 创建模型实例
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    system_instruction="你的系统提示词",
    generation_config={
        'temperature': 0.7,
        'response_mime_type': 'application/json'
    }
)

# 使用模型
response = model.generate_content("Hello, Gemini!")
print(response.text)
```

## 6. API 限制

Google AI Studio 的免费配额：

| 限制类型 | 免费配额 |
| :--- | :--- |
| **每分钟请求数** | 15 次 |
| **每天请求数** | 1,500 次 |
| **每分钟 tokens** | 1,000,000 tokens |
| **每天 tokens** | 1,500,000 tokens |

**注意**: 如果超过限制，你会收到 `429 Too Many Requests` 错误。

## 7. 视频分析特殊说明

### 支持的视频格式

Gemini 1.5 Pro 支持以下视频格式：
- MP4
- MOV
- AVI
- FLV
- MPG
- MPEG
- WMV
- 3GPP

### 视频大小限制

- **最大文件大小**: 2GB
- **最大时长**: 约 1 小时
- **推荐时长**: 2-5 分钟（分析速度更快）

### 上传和处理流程

```python
# 1. 上传视频
video_file = genai.upload_file(path="video.mp4")

# 2. 等待处理完成
import time
while video_file.state.name == "PROCESSING":
    time.sleep(5)
    video_file = genai.get_file(video_file.name)

# 3. 分析视频
response = model.generate_content([video_file, "分析这个视频"])
```

## 8. 常见问题

### Q: 如何查看可用的模型列表？

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
```

### Q: 如何升级到付费版？

1. 访问 https://console.cloud.google.com/
2. 启用 **Generative Language API**
3. 设置计费账户
4. 付费版本的配额会大幅提升

### Q: Google AI Studio API 和 Vertex AI 有什么区别？

| 特性 | Google AI Studio API | Vertex AI |
| :--- | :--- | :--- |
| **适用场景** | 个人开发、原型 | 企业生产环境 |
| **认证方式** | API Key | Service Account |
| **定价** | 免费配额 + 按使用付费 | 按使用付费（无免费配额） |
| **功能** | 基础功能 | 完整功能（包括微调、监控等） |

### Q: 如何处理速率限制？

如果遇到 `429 Too Many Requests` 错误，可以：

1. **添加重试逻辑**:
```python
import time
from google.api_core import retry

@retry.Retry(predicate=retry.if_exception_type(Exception))
def analyze_with_retry():
    return model.generate_content(...)
```

2. **添加延迟**:
```python
import time
time.sleep(4)  # 每次请求间隔 4 秒（15 次/分钟）
```

3. **升级到付费版**

## 9. 总结

使用 Google AI Studio API 的关键点：

1. ✅ 使用正确的模型名称：`gemini-1.5-pro-latest`
2. ✅ 不需要配置 `GEMINI_API_BASE`（使用默认端点）
3. ✅ 注意免费配额限制（15 次/分钟，1500 次/天）
4. ✅ 视频文件建议控制在 2-5 分钟以内

现在你的应用已经完全兼容 Google AI Studio API 了！🎉
