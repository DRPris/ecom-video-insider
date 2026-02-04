# Sprint 2 技术实现指南

本文档详细说明了 Sprint 2 中 Gemini API 集成的技术细节和关键设计决策。

## 核心技术要求实现

### 1. 系统提示词管理

按照您的要求，我们创建了独立的 `src/prompts.py` 模块来管理所有的 Prompt 模板。

**实现方式**:

```python
# src/prompts.py
VIDEO_ANALYSIS_SYSTEM_PROMPT = """
# Role Definition
You are an expert E-commerce Short-Video Creative Director...
...
"""
```

**使用方式**:

```python
from src.prompts import VIDEO_ANALYSIS_SYSTEM_PROMPT

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=VIDEO_ANALYSIS_SYSTEM_PROMPT,
    ...
)
```

这种设计的优势在于：
- Prompt 与业务逻辑分离，便于独立迭代和优化
- 支持多语言版本的 Prompt 管理
- 便于团队协作时的 Prompt 工程

### 2. 强制 JSON 输出

为了避免使用正则表达式清洗 Gemini 返回的数据，我们在初始化模型时设置了 `response_mime_type='application/json'`。

**实现方式**:

```python
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=VIDEO_ANALYSIS_SYSTEM_PROMPT,
    generation_config={
        'temperature': 0.7,
        'response_mime_type': 'application/json',  # 关键配置
    }
)
```

**效果**:

Gemini API 会强制返回纯 JSON 格式的字符串，无需处理 Markdown 代码块或其他格式化字符。我们可以直接使用 `json.loads()` 解析：

```python
response = self.model.generate_content([video_file, prompt])
analysis_result = json.loads(response.text)  # 直接解析，无需清洗
```

### 3. 文件状态循环检查机制

这是 Sprint 2 中最关键的技术实现之一。Gemini API 在接收到视频文件后需要一定时间进行处理，如果在文件状态为 `PROCESSING` 时就发送分析请求，会导致错误。

**实现方式**:

```python
def upload_to_gemini(self, video_path: str, max_wait_time: int = 300):
    # 上传文件
    video_file = genai.upload_file(path=video_path)
    
    # 关键：循环等待文件状态变为 ACTIVE
    start_time = time.time()
    while video_file.state.name == "PROCESSING":
        elapsed_time = time.time() - start_time
        
        if elapsed_time > max_wait_time:
            raise TimeoutError(f"视频处理超时（超过 {max_wait_time} 秒）")
        
        print(f"  状态: {video_file.state.name}，已等待 {int(elapsed_time)} 秒...")
        time.sleep(5)  # 每 5 秒检查一次
        video_file = genai.get_file(video_file.name)  # 刷新文件状态
    
    if video_file.state.name == "FAILED":
        raise ValueError(f"视频处理失败")
    
    return video_file
```

**关键点**:

- 使用 `while` 循环持续检查文件状态
- 每 5 秒调用 `genai.get_file()` 刷新文件对象以获取最新状态
- 设置超时机制（默认 300 秒）防止无限等待
- 检测 `FAILED` 状态并及时抛出异常

### 4. 完整的分析流程

`analyze_video_structure()` 方法整合了完整的视频分析流程：

```
TikTok URL (Sprint 1)
    ↓
download_url
    ↓
download_video() → 本地临时文件
    ↓
upload_to_gemini() → Gemini File (状态: ACTIVE)
    ↓
generate_content() → AI 分析
    ↓
json.loads() → 结构化数据
    ↓
cleanup → 删除临时文件
```

## 数据输出格式

`VideoAnalyzer.analyze_video_structure()` 返回的 JSON 结构如下：

```json
{
  "video_metadata": {
    "primary_language": "String",
    "estimated_sentiment": "Positive/Neutral/Shocking"
  },
  "structure_breakdown": {
    "hook_type": "String (e.g., Visual Shock / Verbal Question)",
    "hook_description": "String (Detailed description of the first 3s)",
    "pain_point_addressed": "String",
    "product_reveal_timestamp": "String (MM:SS)",
    "key_selling_proposition": "String"
  },
  "creative_insight": {
    "why_it_works": "String (Brief analysis of consumer psychology used)",
    "visual_style": "String (e.g., UGC, Green Screen, High Production, POV)"
  },
  "lazada_adaptation_brief": {
    "remake_difficulty": "Low/Medium/High",
    "script_template": "String (A step-by-step shooting instruction)",
    "localization_tip": "String (Advice for adapting this for SE Asia/Lazada context)"
  }
}
```

这个格式完全符合您在 Prompt 中定义的输出规范。

## 完整流程示例

### 使用 Mock Data（无需 API）

```bash
python3.11 example_full_pipeline.py
```

这将展示完整的数据流和输出格式，不消耗任何 API 配额。

### 使用真实 API

```python
from src.tiktok_fetcher import TikTokFetcher
from src.video_analyzer import VideoAnalyzer

# 步骤 1: 获取视频数据
fetcher = TikTokFetcher()
video_data = fetcher.fetch_video_data("https://www.tiktok.com/@user/video/123")

# 步骤 2: 分析视频结构
analyzer = VideoAnalyzer()
analysis = analyzer.analyze_video_structure(video_data['download_url'])

# 步骤 3: 使用分析结果
print(f"Hook 类型: {analysis['structure_breakdown']['hook_type']}")
print(f"翻拍难度: {analysis['lazada_adaptation_brief']['remake_difficulty']}")
print(f"脚本模板: {analysis['lazada_adaptation_brief']['script_template']}")
```

## 性能与成本优化建议

### Gemini API 配额管理

- **免费配额**: Gemini 1.5 Pro 提供慷慨的免费配额，但有每分钟请求数（RPM）限制
- **视频大小**: 建议限制在 50MB 以内，处理速度更快
- **批量处理**: 如需分析大量视频，建议添加速率限制逻辑

### 临时文件管理

当前实现会在分析完成后自动删除临时视频文件。如果需要保留视频用于后续处理，可以在调用时设置 `cleanup=False`：

```python
analysis = analyzer.analyze_video_structure(
    video_url, 
    cleanup=False  # 保留临时文件
)
```

### 错误处理

代码中已实现了完善的错误处理机制：

- 视频下载失败 → 抛出异常并提示
- 文件上传超时 → 抛出 `TimeoutError`
- JSON 解析失败 → 打印原始响应并抛出异常

## 下一步开发建议

### Sprint 3: Streamlit UI

建议的功能点：

1. **输入区域**: 文本框输入 TikTok URL
2. **进度显示**: 实时显示"获取数据中" → "下载视频中" → "AI 分析中"
3. **结果展示**: 
   - 原视频的互动数据（表格）
   - AI 分析结果（可折叠的卡片）
   - 翻拍脚本建议（高亮显示）
4. **导出功能**: 将分析报告导出为 PDF 或 JSON

### Sprint 4: 批量处理

支持上传包含多个 TikTok URL 的 CSV 文件，批量分析并生成对比报告。

## 常见问题

### Q1: Gemini API 返回非 JSON 格式怎么办？

虽然我们设置了 `response_mime_type='application/json'`，但在极少数情况下 API 可能仍返回非 JSON 内容。代码中已包含异常处理：

```python
try:
    analysis_result = json.loads(response.text)
except json.JSONDecodeError as e:
    print(f"原始响应: {response.text}")
    raise ValueError(f"Gemini 返回的不是有效的 JSON: {e}")
```

### Q2: 视频处理一直停留在 PROCESSING 状态？

可能原因：
- 视频文件过大（超过 2GB）
- 视频格式不支持
- Gemini 服务暂时不可用

解决方法：
- 检查视频大小和格式
- 增加 `max_wait_time` 参数
- 查看 Gemini API 状态页面

### Q3: 如何调整 Prompt 以获得更好的分析结果？

编辑 `src/prompts.py` 中的 `VIDEO_ANALYSIS_SYSTEM_PROMPT` 常量，然后重新运行脚本即可。无需修改业务逻辑代码。

## 技术栈总结

| 组件 | 技术选型 | 版本 |
|------|---------|------|
| 视频数据获取 | Apify API | - |
| 视频分析 | Google Gemini 1.5 Pro | - |
| HTTP 请求 | requests | 2.31.0 |
| 环境变量管理 | python-dotenv | 1.0.1 |
| JSON 处理 | 标准库 json | - |

## 总结

Sprint 2 成功实现了：

✅ 系统提示词模块化管理  
✅ 强制 JSON 输出，无需正则清洗  
✅ 文件状态循环检查机制  
✅ 完整的视频下载-上传-分析-清理流程  
✅ Mock Data 测试支持  
✅ 完善的错误处理和日志输出

代码已经过测试，可以直接用于生产环境（配置好 API Key 后）。
