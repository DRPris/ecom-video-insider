# E-Com Video Insider - 配置指南

本文档详细说明如何配置和使用 Sprint 1 数据管道所需的环境变量和 API 密钥。

## 必需的环境变量

### 1. APIFY_API_TOKEN

**用途**: 用于调用 Apify 平台的 TikTok Scraper Actor，获取视频元数据和下载链接。

**获取步骤**:

1. 访问 [Apify 官网](https://apify.com/) 并注册账号（如果还没有）
2. 登录后，进入 [Apify Console](https://console.apify.com/)
3. 点击右上角的头像，选择 **Settings**
4. 在左侧菜单中选择 **Integrations**
5. 找到 **API Token** 部分，点击 **Generate new token** 或复制现有 Token
6. 将该 Token 复制到 `.env` 文件中的 `APIFY_API_TOKEN` 字段

**注意事项**:
- Apify 提供免费套餐，每月有一定的免费计算单元（Compute Units）
- 每次调用 TikTok Scraper 会消耗少量计算单元，请注意配额
- 不要将 Token 提交到公开的代码仓库中

### 2. GEMINI_API_KEY (Sprint 2 必需)

**用途**: 用于调用 Google Gemini 1.5 Pro API 进行视频内容分析和脚本生成。

**获取步骤**:

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用您的 Google 账号登录
3. 点击 **Create API Key** 按钮
4. 选择一个 Google Cloud 项目（或创建新项目）
5. 复制生成的 API Key
6. 将该 Key 复制到 `.env` 文件中的 `GEMINI_API_KEY` 字段

**注意事项**:
- Gemini API 目前提供免费配额，但有请求速率限制（RPM）
- Gemini 1.5 Pro 支持原生视频输入，最大支持 2GB 文件
- Sprint 2 中此 API 为必需配置

## 配置步骤

### 步骤 1: 创建 .env 文件

```bash
cd /home/ubuntu/ecom-video-insider
cp .env.example .env
```

### 步骤 2: 编辑 .env 文件

使用任意文本编辑器打开 `.env` 文件，填入您的 API 密钥：

```dotenv
# Apify API Token
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini API Key
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 步骤 3: 验证配置

运行测试脚本来验证配置是否正确：

```bash
python3.11 src/tiktok_fetcher.py
```

如果看到 Mock Data 测试成功输出，说明基础环境配置正确。

要测试真实 API 调用，请修改 `src/tiktok_fetcher.py` 中的 `main()` 函数，取消注释真实 API 测试部分，并替换为一个真实的 TikTok 视频 URL。

## 常见问题

### Q1: 提示 "APIFY_API_TOKEN 未设置" 错误

**原因**: `.env` 文件未创建或未正确配置。

**解决方法**: 
- 确保 `.env` 文件存在于项目根目录
- 检查 `.env` 文件中是否正确填写了 `APIFY_API_TOKEN`
- 确保没有多余的空格或引号

### Q2: Apify Actor 运行失败

**可能原因**:
- API Token 无效或已过期
- Apify 账号计算单元不足
- TikTok 视频 URL 格式不正确或视频已被删除

**解决方法**:
- 检查 API Token 是否正确
- 登录 Apify Console 查看账号余额
- 尝试使用其他 TikTok 视频 URL 进行测试

### Q3: 如何选择合适的 Apify Actor?

本项目默认使用 `clockworks/tiktok-scraper`，这是一个流行且稳定的 TikTok 数据抓取 Actor。如果您需要使用其他 Actor，可以修改 `src/tiktok_fetcher.py` 中的 `self.actor_id` 变量。

在 [Apify Store](https://apify.com/store) 中搜索 "TikTok" 可以找到其他可用的 Actor。

## 安全建议

- **永远不要**将 `.env` 文件提交到 Git 仓库
- 在 `.gitignore` 中添加 `.env` 以防止意外提交
- 定期轮换 API Token
- 如果 Token 泄露，立即在 Apify Console 中撤销并生成新的 Token

## 技术支持

如果在配置过程中遇到问题，请参考：
- [Apify 官方文档](https://docs.apify.com/)
- [Google Gemini API 文档](https://ai.google.dev/docs)
