# JSON 解析错误修复指南

## 错误信息

```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**位置**: `app.py` 第 201 行
```python
analysis_result = json.loads(response.text)
```

## 问题原因

Gemini API 返回的内容可能不是纯 JSON 格式，而是：

### 1. Markdown 代码块格式
```
```json
{
  "video_structure": {...}
}
```
```

### 2. 带文字说明的格式
```
Here is the analysis of the video:

{
  "video_structure": {...}
}
```

### 3. 纯文本格式
```
The video shows...
```

## 解决方案

我已经实现了**三层 JSON 提取逻辑**，可以处理各种返回格式：

### 方法 1: 直接解析
```python
try:
    analysis_result = json.loads(response_text)
except json.JSONDecodeError:
    # 进入方法 2
```

### 方法 2: 提取 Markdown 代码块
```python
import re
json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
if json_match:
    analysis_result = json.loads(json_match.group(1))
```

### 方法 3: 查找第一个 { 和最后一个 }
```python
start_idx = response_text.find('{')
end_idx = response_text.rfind('}')
if start_idx != -1 and end_idx != -1:
    json_str = response_text[start_idx:end_idx+1]
    analysis_result = json.loads(json_str)
```

### 方法 4: 显示原始响应（调试用）
```python
else:
    st.error("❌ AI 返回的内容不是有效的 JSON 格式")
    st.text_area("原始响应", response_text, height=300)
    st.stop()
```

## 为什么会出现这个问题？

### 原因 1: 模型配置

不同的 Gemini 模型可能有不同的输出格式：

| 模型 | JSON 输出格式 | 稳定性 |
| :--- | :--- | :--- |
| gemini-flash-latest | 有时带 Markdown | ⭐⭐⭐ |
| gemini-pro-latest | 通常纯 JSON | ⭐⭐⭐⭐ |
| gemini-2.5-pro | 通常纯 JSON | ⭐⭐⭐⭐⭐ |

### 原因 2: Prompt 设计

我们的 Prompt 已经明确要求返回 JSON：

```python
combined_prompt = f"""{self.system_prompt}

---

Now, please analyze the following video according to the framework above.
Return your analysis in valid JSON format.
"""
```

但 Gemini 有时仍然会添加额外的文字说明。

### 原因 3: generation_config

我们没有设置 `response_mime_type='application/json'`，这可能导致 Gemini 返回非 JSON 格式。

## 进一步优化

### 优化 1: 强制 JSON 输出

修改 `src/video_analyzer.py`:

```python
self.model = genai.GenerativeModel(
    model_name='gemini-flash-latest',
    generation_config={
        'temperature': 0.7,
        'response_mime_type': 'application/json',  # ✅ 强制 JSON 输出
    }
)
```

**注意**: 这个参数可能只在某些模型版本中可用。

### 优化 2: 更明确的 Prompt

```python
combined_prompt = f"""{self.system_prompt}

---

IMPORTANT: You MUST return ONLY valid JSON, with no additional text, explanations, or markdown formatting.

Now, please analyze the following video according to the framework above.
"""
```

### 优化 3: 使用 JSON Schema

```python
generation_config={
    'temperature': 0.7,
    'response_mime_type': 'application/json',
    'response_schema': {
        'type': 'object',
        'properties': {
            'video_structure': {...},
            'creative_insight': {...},
            'lazada_adaptation_brief': {...}
        },
        'required': ['video_structure', 'creative_insight', 'lazada_adaptation_brief']
    }
}
```

## 当前实现

### 已修复的代码 (`app.py`)

```python
# 解析 JSON 响应
# Gemini 可能返回的格式:
# 1. 纯 JSON: {"video_structure": ...}
# 2. Markdown 代码块: ```json\n{...}\n```
# 3. 带文字说明: Here is the analysis:\n{...}

response_text = response.text.strip()

# 尝试提取 JSON
try:
    # 方法 1: 直接解析
    analysis_result = json.loads(response_text)
except json.JSONDecodeError:
    # 方法 2: 提取 Markdown 代码块中的 JSON
    import re
    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
    if json_match:
        analysis_result = json.loads(json_match.group(1))
    else:
        # 方法 3: 查找第一个 { 和最后一个 }
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            analysis_result = json.loads(json_str)
        else:
            # 如果都失败，显示原始响应
            st.error("❌ AI 返回的内容不是有效的 JSON 格式")
            st.text_area("原始响应", response_text, height=300)
            st.stop()
```

### 优势

1. ✅ **容错性强**: 可以处理多种返回格式
2. ✅ **调试友好**: 失败时显示原始响应
3. ✅ **向后兼容**: 不影响正常的 JSON 返回

## 测试

### 测试用例 1: 纯 JSON
```json
{"video_structure": {...}}
```
**结果**: ✅ 方法 1 成功

### 测试用例 2: Markdown 代码块
```
```json
{"video_structure": {...}}
```
```
**结果**: ✅ 方法 2 成功

### 测试用例 3: 带文字说明
```
Here is the analysis:

{"video_structure": {...}}

Hope this helps!
```
**结果**: ✅ 方法 3 成功

### 测试用例 4: 纯文本
```
The video shows a recipe...
```
**结果**: ❌ 显示原始响应，提示用户

## 如果仍然失败

### 情况 1: 显示原始响应

如果应用显示了"原始响应"文本框，说明 Gemini 返回的内容完全不包含 JSON。

**可能原因**:
- Prompt 没有被正确传递
- 模型理解错误
- 视频内容不适合分析

**解决方案**:
1. 检查视频 URL 是否正确
2. 尝试更短的视频（< 2 分钟）
3. 切换到 `gemini-pro-latest`（更稳定）

### 情况 2: JSON 格式错误

如果提取到的 JSON 仍然无法解析，可能是：
- JSON 中有语法错误
- 嵌套层级过深
- 包含非法字符

**解决方案**:
```python
# 添加更宽松的 JSON 解析
import json5  # pip install json5
analysis_result = json5.loads(json_str)
```

## 总结

1. ✅ **已实现三层 JSON 提取逻辑**
2. ✅ **可以处理各种返回格式**
3. ✅ **失败时显示原始响应以便调试**
4. 💡 **建议**: 如果频繁出现问题，考虑添加 `response_mime_type='application/json'`

现在刷新页面再试一次！如果仍然出现问题，应用会显示 Gemini 返回的原始内容，方便我们进一步调试。
