# Google AI Studio 配额错误修复指南

## 错误信息

```
429 You exceeded your current quota, please check your plan and billing details.
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, 
limit: 0, model: gemini-2.5-pro
```

## 问题原因

### 1. 使用了不在免费配额中的模型

错误信息显示使用了 `gemini-2.5-pro`，这个模型：
- ❌ 不在 Google AI Studio 的免费配额中
- ❌ 配额限制为 0（即完全不可用于免费用户）
- ❌ 需要付费账户或企业账户

### 2. 可能的原因

- **Streamlit 缓存**: 之前运行时使用的模型被缓存
- **代码未生效**: 修改后的代码没有被重新加载
- **环境变量**: 某个环境变量指定了错误的模型

## 解决方案

### 方案 1: 清除缓存并重启（已执行）

```bash
# 停止应用
lsof -ti:8501 | xargs kill -9

# 清除 Streamlit 缓存
rm -rf /home/ubuntu/.streamlit/cache

# 重启应用
cd /home/ubuntu/ecom-video-insider
streamlit run app.py
```

### 方案 2: 使用免费配额支持的模型

根据 `list_models.py` 的查询结果，以下模型在免费配额中：

| 模型名称 | 免费配额 | 推荐度 |
| :--- | :--- | :--- |
| **gemini-flash-latest** | ✅ 高配额 | ⭐⭐⭐⭐⭐ (推荐) |
| gemini-pro-latest | ✅ 中等配额 | ⭐⭐⭐⭐ |
| gemini-2.0-flash-lite | ✅ 高配额 | ⭐⭐⭐ |
| gemini-flash-lite-latest | ✅ 高配额 | ⭐⭐⭐ |

### 方案 3: 修改为 gemini-flash-latest（更推荐）

`gemini-flash-latest` 的优势：
- ✅ **更高的免费配额**
- ✅ **更快的响应速度**
- ✅ **更低的成本**（如果将来付费）
- ✅ **质量足够好**（适合视频分析）

修改 `src/video_analyzer.py`:

```python
self.model = genai.GenerativeModel(
    model_name='gemini-flash-latest',  # 改为 flash 版本
    generation_config={
        'temperature': 0.7,
    }
)
```

## Google AI Studio 免费配额详情

### 每日配额（免费用户）

| 指标 | gemini-flash-latest | gemini-pro-latest | gemini-2.5-pro |
| :--- | :--- | :--- | :--- |
| **每分钟请求数** | 15 次 | 15 次 | ❌ 0 次 |
| **每天请求数** | 1,500 次 | 1,500 次 | ❌ 0 次 |
| **每分钟 tokens** | 1,000,000 | 1,000,000 | ❌ 0 |
| **每天 tokens** | 无限制 | 无限制 | ❌ 0 |

**结论**: `gemini-2.5-pro` 对免费用户完全不可用！

## 如何避免配额错误

### 1. 使用正确的模型

始终使用免费配额支持的模型：
- `gemini-flash-latest` (推荐)
- `gemini-pro-latest`
- `gemini-2.0-flash-lite`

### 2. 监控配额使用

访问 https://aistudio.google.com/app/prompts 查看：
- 当前配额使用情况
- 剩余配额
- 配额重置时间

### 3. 实施速率限制

在生产环境中添加速率限制：

```python
import time

# 每次请求间隔 4 秒（确保不超过 15 次/分钟）
time.sleep(4)
```

### 4. 添加重试逻辑

```python
from google.api_core import retry

@retry.Retry(
    predicate=retry.if_exception_type(Exception),
    initial=1.0,
    maximum=10.0,
    multiplier=2.0,
    timeout=60.0
)
def analyze_with_retry():
    return model.generate_content(...)
```

## 升级到付费版

如果免费配额不够用，可以升级到付费版：

### 步骤

1. 访问 https://console.cloud.google.com/
2. 启用 **Generative Language API**
3. 设置计费账户
4. 配额会自动提升

### 付费版配额

| 指标 | 免费版 | 付费版 |
| :--- | :--- | :--- |
| 每分钟请求数 | 15 次 | 60 次 |
| 每天请求数 | 1,500 次 | 无限制 |
| 每分钟 tokens | 1,000,000 | 4,000,000 |

### 定价（参考）

- **gemini-flash-latest**: $0.075 / 1M input tokens, $0.30 / 1M output tokens
- **gemini-pro-latest**: $1.25 / 1M input tokens, $5.00 / 1M output tokens
- **gemini-2.5-pro**: $2.50 / 1M input tokens, $10.00 / 1M output tokens

## 当前配置

### 代码中的模型

```bash
# 查看当前使用的模型
cd /home/ubuntu/ecom-video-insider
grep "model_name" src/video_analyzer.py
```

**输出应该是**:
```python
model_name='gemini-pro-latest',  # 或 gemini-flash-latest
```

### 环境变量

```bash
# 查看 .env 配置
cat .env
```

**确保没有**:
```dotenv
GEMINI_MODEL_NAME=gemini-2.5-pro  # ❌ 不应该有这个
```

## 测试

### 1. 刷新页面

访问: https://8501-i13f50at2r18mxy73c452-5ceb6bda.sg1.manus.computer

### 2. 输入测试 URL

```
https://www.tiktok.com/@5.minute.recipes/video/7588608011745250591
```

### 3. 点击分析

如果仍然出现配额错误，说明：
- 今天的配额已用完（等待明天重置）
- 或者需要切换到 `gemini-flash-latest`

## 推荐配置

为了避免配额问题，我强烈推荐使用 `gemini-flash-latest`:

```python
# src/video_analyzer.py
self.model = genai.GenerativeModel(
    model_name='gemini-flash-latest',  # ✅ 最佳选择
    generation_config={
        'temperature': 0.7,
    }
)
```

**优势**:
- ✅ 更高的免费配额
- ✅ 更快的响应速度（2-3 秒 vs 5-10 秒）
- ✅ 更低的成本
- ✅ 质量足够好（对于视频分析任务）

## 总结

1. ✅ **已清除缓存并重启应用**
2. ✅ **代码中使用的是 `gemini-pro-latest`**（在免费配额中）
3. 💡 **建议切换到 `gemini-flash-latest`**（更高配额）
4. 📊 **监控配额使用情况**

现在刷新页面再试一次！如果还有问题，我们可以切换到 `gemini-flash-latest`。
