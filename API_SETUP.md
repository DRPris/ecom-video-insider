# API Key 配置指南

本文档说明如何配置 API Keys，使其在刷新页面后自动加载，无需重复填写。

## 方法 1: 使用 .env 文件（推荐）

### 步骤 1: 编辑 .env 文件

在项目根目录下已经有一个 `.env` 文件，使用文本编辑器打开它：

```bash
nano /home/ubuntu/ecom-video-insider/.env
# 或者
vim /home/ubuntu/ecom-video-insider/.env
```

### 步骤 2: 填写你的 API Keys

```dotenv
# Apify API Token (必需)
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini API Key (必需)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini API Base URL (可选，使用 Google 官方 API 时留空)
GEMINI_API_BASE=
```

### 步骤 3: 保存并重启应用

```bash
# 重启 Streamlit 应用
cd /home/ubuntu/ecom-video-insider
streamlit run app.py
```

### 步骤 4: 刷新页面

打开浏览器，刷新页面，你会看到侧边栏的输入框已经自动填充了你的 API Keys！

## 方法 2: 使用环境变量

如果你在服务器上部署，可以直接设置环境变量：

```bash
export APIFY_API_TOKEN="apify_api_xxxxxxxxx"
export GEMINI_API_KEY="AIzaSyxxxxxxxxx"
export GEMINI_API_BASE=""  # 可选
```

然后启动应用：

```bash
streamlit run app.py
```

## 如何获取 API Keys

### 1. Apify API Token

1. 访问 https://console.apify.com/
2. 登录你的账号
3. 点击右上角头像 → **Settings**
4. 在左侧菜单选择 **Integrations**
5. 找到 **Personal API tokens** 部分
6. 点击 **Add new token**
7. 复制生成的 Token（格式：`apify_api_xxxxxxxxx`）

### 2. Google Gemini API Key

1. 访问 https://aistudio.google.com/app/apikey
2. 登录你的 Google 账号
3. 点击 **Create API Key**
4. 选择一个 Google Cloud 项目（或创建新项目）
5. 复制生成的 API Key（格式：`AIzaSyxxxxxxxxx`）

**注意**: Gemini API 有免费配额限制：
- 每分钟 15 次请求
- 每天 1500 次请求
- 每分钟 100 万 tokens

## 安全建议

### 1. 不要提交 .env 文件到 Git

`.env` 文件已经在 `.gitignore` 中，确保不会被提交到版本控制系统。

### 2. 定期更换 API Keys

如果你怀疑 API Key 泄露，立即在相应平台上撤销并重新生成。

### 3. 使用环境变量（生产环境）

在生产环境中，建议使用系统环境变量或密钥管理服务（如 AWS Secrets Manager、HashiCorp Vault）。

## 验证配置

### 检查 .env 文件是否被正确加载

在 `app.py` 中添加调试代码：

```python
import os
from dotenv import load_dotenv

load_dotenv()

print(f"APIFY_API_TOKEN: {os.getenv('APIFY_API_TOKEN')[:20]}...")  # 只打印前 20 个字符
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20]}...")
```

### 测试 API 连接

#### 测试 Apify API

```bash
curl "https://api.apify.com/v2/acts" \
     -H "Authorization: Bearer YOUR_APIFY_TOKEN"
```

#### 测试 Gemini API

```bash
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_GEMINI_KEY"
```

## 常见问题

### Q: 为什么刷新后 API Key 还是空的？

**A**: 可能的原因：

1. **.env 文件位置不对**
   - 确保 `.env` 文件在项目根目录（`/home/ubuntu/ecom-video-insider/.env`）
   - 与 `app.py` 在同一目录

2. **.env 文件格式错误**
   - 确保没有多余的空格：`APIFY_API_TOKEN=xxx`（不是 `APIFY_API_TOKEN = xxx`）
   - 确保没有引号：`APIFY_API_TOKEN=xxx`（不是 `APIFY_API_TOKEN="xxx"`）

3. **没有重启应用**
   - 修改 `.env` 文件后需要重启 Streamlit 应用

### Q: 可以在侧边栏修改 API Key 吗？

**A**: 可以！侧边栏的输入框会显示 `.env` 文件中的值作为默认值，你可以：
- 直接在输入框中修改（临时修改，刷新后会恢复为 `.env` 中的值）
- 或者修改 `.env` 文件（永久修改）

### Q: 如何隐藏 API Key？

**A**: 输入框已经设置为 `type="password"`，显示为密码遮罩（`••••••••`）。

### Q: 多个用户如何使用不同的 API Key？

**A**: 有两种方案：

1. **每个用户在侧边栏输入自己的 API Key**（不保存到 `.env`）
2. **部署多个实例**，每个实例使用不同的 `.env` 文件

## 生产环境部署

### 使用 Docker

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - APIFY_API_TOKEN=${APIFY_API_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_API_BASE=${GEMINI_API_BASE}
    env_file:
      - .env
```

### 使用 Streamlit Cloud

1. 在 Streamlit Cloud 的项目设置中添加 **Secrets**
2. 格式与 `.env` 文件相同
3. Streamlit 会自动加载这些密钥

### 使用 Heroku

```bash
heroku config:set APIFY_API_TOKEN=xxx
heroku config:set GEMINI_API_KEY=xxx
```

## 总结

使用 `.env` 文件配置 API Keys 的优势：

- ✅ **方便**: 只需配置一次，刷新页面自动加载
- ✅ **安全**: 不会被提交到 Git
- ✅ **灵活**: 可以随时在侧边栏临时修改
- ✅ **标准**: 符合 12-Factor App 最佳实践

现在你可以专注于使用应用，而不用每次都重新输入 API Keys 了！🎉
