# 🎤 OpenAI Whisper API 配置指南

## 为什么使用 Whisper API？

**OpenAI Whisper** 是专业的语音识别 API，相比 Gemini 的音频理解功能：

✅ **更准确**：专门为语音识别优化  
✅ **更稳定**：成熟的商业 API  
✅ **支持时间戳**：自动分段并提供精确时间戳  
✅ **多语言支持**：支持 99 种语言  
✅ **价格实惠**：$0.006 / 分钟（约 ¥0.04 / 分钟）

---

## 价格参考

| 视频时长 | 费用（美元） | 费用（人民币） |
|---------|------------|--------------|
| 1 分钟   | $0.006     | ¥0.04        |
| 10 分钟  | $0.06      | ¥0.4         |
| 100 个 1 分钟视频 | $0.6 | ¥4 |

**非常实惠！** 即使每天分析 100 个视频，一个月也只需要 ¥120 左右。

---

## 配置步骤

### 1. 获取 OpenAI API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录或注册账号
3. 点击 **"Create new secret key"**
4. 复制生成的 API Key（格式：`sk-proj-xxxxx`）

### 2. 充值账户

1. 访问 [Billing](https://platform.openai.com/account/billing/overview)
2. 点击 **"Add payment method"**
3. 最低充值 $5（约 ¥35）

### 3. 配置到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 找到您的应用 → **Settings** → **Secrets**
3. 添加以下内容：

```toml
# 现有的配置
APIFY_API_TOKEN = "apify_api_xxxxx"
GEMINI_API_KEY = "AIzaSyxxxxx"
APP_PASSWORD = "your_password"

# 新增：OpenAI API Key
OPENAI_API_KEY = "sk-proj-xxxxx"
```

4. 点击 **"Save"**，应用会自动重启

---

## 工作原理

应用会**自动选择最佳转录方法**：

1. **优先使用 Whisper API**（如果已配置）
   - 准确率高
   - 自动生成时间戳
   
2. **备选使用 Gemini**（如果 Whisper 不可用）
   - 免费
   - 但可能不稳定

---

## 验证配置

配置完成后，重新分析一个视频：

1. 在应用中输入 TikTok 视频链接
2. 点击 **"Analyze Now"**
3. 查看 **"口播摘录"** 标签页
4. 如果看到带时间戳的转录文本，说明配置成功！

---

## 常见问题

### Q: 我必须配置 Whisper API 吗？

**A:** 不是必须的。如果不配置，应用会使用 Gemini 进行转录（免费但可能不稳定）。

### Q: 如果我不想付费怎么办？

**A:** 可以不配置 OpenAI API Key，应用会自动使用 Gemini。但转录成功率可能较低。

### Q: 如何查看 API 使用量？

**A:** 访问 [OpenAI Usage](https://platform.openai.com/usage) 查看详细使用统计。

### Q: 支持哪些语言？

**A:** Whisper 支持 99 种语言，包括中文、英文、日文、韩文等。

---

## 技术细节

- **模型**：`whisper-1`
- **响应格式**：`verbose_json`（包含时间戳）
- **分段粒度**：按句子/段落自动分段
- **时间戳格式**：`MM:SS`

---

**配置完成后，您的视频口播转录功能将更加准确和稳定！** 🎉
