# KIE API 配置指南

本文档说明如何配置应用以使用 KIE API 或其他代理服务来接入 Google Gemini API。

## 什么是 KIE API？

KIE API 是一种代理服务，允许您通过自定义的 API 端点访问 Google Gemini API。这在以下场景中非常有用：

- 需要通过企业代理访问 API
- 使用第三方 API 网关
- 需要添加额外的认证或日志记录层
- 在某些地区无法直接访问 Google API

## 配置方式

### 方式 1: 在 Web 界面中配置

1. 启动应用后，在侧边栏找到以下配置项：
   - **Gemini API Key**: 输入您的 API Key 或 KIE API Token
   - **Gemini API Base URL (可选)**: 输入完整的 KIE API 端点 URL

2. 示例配置：
   ```
   Gemini API Key: your_kie_api_token_here
   Gemini API Base URL: https://your-kie-api-endpoint.com/v1
   ```

3. 点击"🚀 Analyze Now"按钮即可使用 KIE API 进行分析。

### 方式 2: 在 .env 文件中配置

1. 编辑项目根目录下的 `.env` 文件：

```dotenv
# Apify API Token
APIFY_API_TOKEN=your_apify_token_here

# Gemini API Key 或 KIE API Token
GEMINI_API_KEY=your_kie_api_token_here

# KIE API Base URL
GEMINI_API_BASE=https://your-kie-api-endpoint.com/v1
```

2. 保存文件后重启应用。

## 技术实现

### 后端代码修改

在 `src/video_analyzer.py` 中，我们修改了 `VideoAnalyzer` 类的初始化方法：

```python
def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
    self.api_key = api_key or os.getenv('GEMINI_API_KEY')
    self.api_base = api_base or os.getenv('GEMINI_API_BASE')
    
    # 配置 Gemini API
    if self.api_base:
        # 使用自定义 API Base URL（KIE API）
        genai.configure(
            api_key=self.api_key,
            transport='rest',
            client_options={'api_endpoint': self.api_base}
        )
    else:
        # 使用默认 Google API
        genai.configure(api_key=self.api_key)
```

### 前端界面修改

在 `app.py` 中，我们在侧边栏添加了新的输入框：

```python
gemini_key = st.text_input(
    "Gemini API Key", 
    type="password",
    help="API Key 或 KIE API Token"
)

gemini_base = st.text_input(
    "Gemini API Base URL (可选)",
    placeholder="https://your-kie-api-endpoint.com/v1",
    help="如果使用 KIE API 或其他代理服务，请输入完整的 API Base URL"
)
```

在调用 `VideoAnalyzer` 时传入 `api_base` 参数：

```python
analyzer = VideoAnalyzer(
    api_key=gemini_key,
    api_base=gemini_base if gemini_base else None
)
```

## 常见问题

### Q1: 如何知道我的 KIE API 端点 URL？

请联系您的 KIE API 服务提供商获取完整的端点 URL。通常格式为：

```
https://your-domain.com/v1
https://api.your-service.com/gemini/v1
```

### Q2: 是否必须填写 API Base URL？

不是必须的。如果您留空 "Gemini API Base URL" 字段，应用将使用 Google 官方的 API 端点。

### Q3: 如何验证 KIE API 配置是否正确？

在应用启动时，控制台会打印以下信息之一：

- `✅ 使用自定义 API Base: https://your-kie-api-endpoint.com/v1` - 表示正在使用 KIE API
- `✅ 使用 Google 官方 API` - 表示正在使用 Google 官方 API

### Q4: KIE API 和 Google API 有什么区别？

从功能角度来说，两者完全相同。KIE API 只是一个代理层，最终仍然调用 Google Gemini API。主要区别在于：

- **网络路径**: KIE API 可能通过不同的网络路径访问
- **认证方式**: KIE API 可能使用不同的 Token 格式
- **额外功能**: KIE API 可能提供额外的日志、监控或计费功能

## 测试配置

### 使用 Mock Data 测试

即使配置了 KIE API，您仍然可以使用后端脚本进行测试：

```bash
cd /home/ubuntu/ecom-video-insider
python3.11 example_full_pipeline.py
```

### 使用真实 API 测试

1. 在 `.env` 文件中配置 KIE API 信息
2. 启动 Web 应用
3. 输入一个 TikTok 视频 URL
4. 点击分析按钮

如果配置正确，应用将通过 KIE API 调用 Gemini 进行分析。

## 故障排查

### 错误: "GEMINI_API_KEY 未设置"

**原因**: 未提供 API Key。

**解决**: 在侧边栏的 "Gemini API Key" 字段中输入您的 Token。

### 错误: "Connection refused" 或 "API endpoint not found"

**原因**: API Base URL 配置错误或 KIE API 服务不可用。

**解决**: 
1. 检查 API Base URL 是否正确
2. 确认 KIE API 服务正在运行
3. 尝试使用 `curl` 命令测试端点可达性

### 错误: "Invalid API key"

**原因**: API Key 或 Token 无效。

**解决**: 
1. 确认您使用的是正确的 KIE API Token
2. 检查 Token 是否已过期
3. 联系 KIE API 服务提供商验证 Token

## 总结

通过添加 `api_base` 参数支持，E-Com Video Insider 现在可以灵活地使用 Google 官方 API 或任何兼容的代理服务（如 KIE API）。这为企业用户和需要特殊网络配置的用户提供了更大的灵活性。
