# Google AI Studio API (v1) 兼容性修复指南

**版本**: 1.1
**作者**: Manus AI
**日期**: 2026-02-04

## 问题描述

当使用从 Google AI Studio 获取的 API Key 时，应用会报错：

```
NotFound: 404 models/gemini-1.5-pro-latest is not found for API version v1beta, 
or is not supported for generateContent.
```

## 根本原因

Google Generative AI SDK 的 `system_instruction` 参数会强制使用 **beta 版本 (v1beta)** 的 API。然而，从 Google AI Studio 获取的 API Key 只能访问**稳定版 (v1)** API，不支持 v1beta。

### API 版本对比

| API 版本 | 端点 | 支持 system_instruction | 获取方式 |
| :--- | :--- | :--- | :--- |
| **v1 (稳定版)** | `generativelanguage.googleapis.com/v1` | ❌ 不支持 | Google AI Studio |
| **v1beta (测试版)** | `generativelanguage.googleapis.com/v1beta` | ✅ 支持 | Vertex AI / 企业账户 |

## 解决方案

移除 `GenerativeModel` 初始化时的 `system_instruction` 参数，改为将系统提示词与用户提示词组合在一起发送。

### 修改前（错误）

```python
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    system_instruction=VIDEO_ANALYSIS_SYSTEM_PROMPT,  # ❌ 强制使用 v1beta
    generation_config={
        'temperature': 0.7,
        'response_mime_type': 'application/json',
    }
)

# 调用时
response = self.model.generate_content([video_file, "Analyze this video"])
```

### 修改后（正确）

```python
# 初始化时不使用 system_instruction
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    generation_config={
        'temperature': 0.7,
    }
)

# 保存系统提示词
self.system_prompt = VIDEO_ANALYSIS_SYSTEM_PROMPT

# 调用时组合系统提示词和用户提示词
combined_prompt = f"""{self.system_prompt}

---

Now, please analyze the following video according to the framework above.
Return your analysis in valid JSON format.
"""

response = self.model.generate_content([video_file, combined_prompt])
```

## 已修改的文件

### 1. `src/video_analyzer.py`

**修改位置 1**: 模型初始化（第 61-72 行）

```python
# 使用 Gemini 1.5 Pro（支持长视频输入）
# 注意: 移除 system_instruction 以兼容 Google AI Studio 的稳定版 API (v1)
# system_instruction 会强制使用 v1beta API，导致 404 错误
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    generation_config={
        'temperature': 0.7,
    }
)

# 保存系统提示词，稍后与用户提示词组合使用
self.system_prompt = VIDEO_ANALYSIS_SYSTEM_PROMPT
```

**修改位置 2**: 调用模型（第 228-241 行）

```python
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
```

### 2. `app.py`

**修改位置**: 调用模型（第 189-198 行）

```python
# 调用 Gemini 进行分析
# 组合系统提示词和用户提示词
combined_prompt = f"""{analyzer.system_prompt}

---

Now, please analyze the following video according to the framework above.
Return your analysis in valid JSON format.
"""
response = analyzer.model.generate_content([video_file, combined_prompt])
```

## 为什么这样修复有效？

1. **避免 v1beta 依赖**: 移除 `system_instruction` 后，SDK 会自动使用稳定版 (v1) API。

2. **功能等价**: 将系统提示词作为消息的一部分发送，效果与 `system_instruction` 相同。

3. **更好的兼容性**: 这种方式适用于所有 API 版本，包括 v1 和 v1beta。

## 验证修复

### 步骤 1: 确认 API Key 来源

确保你的 API Key 是从 Google AI Studio 获取的：
- 访问 https://aistudio.google.com/app/apikey
- API Key 格式：`AIzaSy...`

### 步骤 2: 配置 .env 文件

```dotenv
APIFY_API_TOKEN=apify_api_你的token
GEMINI_API_KEY=AIzaSy你的key
GEMINI_API_BASE=  # 留空
```

### 步骤 3: 测试应用

1. 启动应用：
```bash
cd /home/ubuntu/ecom-video-insider
streamlit run app.py
```

2. 在侧边栏填写 API Keys

3. 输入 TikTok URL 并分析

4. 如果看到以下输出，说明修复成功：
```
✅ 使用 Google 官方 API
🎬 开始视频结构分析
📥 正在使用 yt-dlp 下载视频...
✅ 视频下载完成
🚀 正在上传到 Gemini API 并分析...
🤖 开始 AI 分析...
✅ 分析完成！
```

## 常见问题

### Q: 为什么不直接使用 Vertex AI？

**A**: Vertex AI 需要：
- Google Cloud 企业账户
- 复杂的 Service Account 认证
- 更高的成本

Google AI Studio 更适合个人开发和快速原型。

### Q: 移除 system_instruction 会影响分析质量吗？

**A**: **不会**。将系统提示词作为消息的一部分发送，效果与 `system_instruction` 完全相同。Gemini 会同样理解和遵循指令。

### Q: 如果我有 Vertex AI 账户，可以使用 system_instruction 吗？

**A**: 可以！如果你使用 Vertex AI，可以恢复 `system_instruction` 参数。但需要：

1. 修改认证方式为 Service Account
2. 使用 Vertex AI 的端点
3. 模型名称改为 `gemini-1.5-pro`（不是 `-latest`）

### Q: response_mime_type='application/json' 为什么也被移除了？

**A**: 这个参数也是 v1beta 特有的。在 v1 API 中，我们通过在 prompt 中明确要求 "Return your analysis in valid JSON format" 来实现相同效果。

## 技术细节

### SDK 版本检测逻辑

Google Generative AI SDK 的版本选择逻辑：

```python
# 伪代码
if model_config.has('system_instruction'):
    api_version = 'v1beta'  # 使用测试版 API
else:
    api_version = 'v1'  # 使用稳定版 API
```

### 为什么 Google 这样设计？

- **v1 (稳定版)**: 保证向后兼容，功能稳定，适合生产环境
- **v1beta (测试版)**: 提供最新功能（如 `system_instruction`），但可能有破坏性变更

`system_instruction` 是较新的功能，目前只在 beta 版本中可用。

## 总结

这次修复的核心是：**不使用 beta 版本特有的功能，确保代码兼容 Google AI Studio 的稳定版 API**。

修改后的代码：
- ✅ 兼容 Google AI Studio API (v1)
- ✅ 保持相同的分析质量
- ✅ 无需更改 API Key 或认证方式
- ✅ 代码更简洁，更易维护

现在你可以放心使用 Google AI Studio 的免费配额进行开发和测试了！🎉
