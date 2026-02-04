# 🔐 安全最佳实践指南

## API Key 安全管理

### ✅ 正确的做法

1. **使用环境变量或 Secrets 管理**
   - Streamlit Cloud: 使用 Settings → Secrets
   - 本地开发: 使用 `.env` 文件（已在 `.gitignore` 中排除）

2. **永远不要硬编码 API Keys**
   ```python
   # ❌ 错误
   api_key = "AIzaSyA94zOsGcxJP1bFxEyirf1SrNv4P-IGv8E"
   
   # ✅ 正确
   api_key = os.getenv('GEMINI_API_KEY')
   ```

3. **文档中使用占位符**
   ```toml
   # ✅ 正确
   GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # ❌ 错误
   GEMINI_API_KEY=AIzaSyA94zOsGcxJP1bFxEyirf1SrNv4P-IGv8E
   ```

4. **定期轮换 API Keys**
   - 建议每 1-3 个月更换一次
   - 如果怀疑泄露，立即更换

---

## ❌ 常见泄露途径

### 1. 提交到 Git 仓库
- 硬编码在代码中
- 写在文档文件中
- `.env` 文件未被 `.gitignore` 排除

### 2. 公开分享
- 聊天记录、邮件、论坛
- 截图中包含 API Key
- 日志文件中打印 API Key

### 3. 第三方工具
- 浏览器插件记录
- 云端同步工具
- 代码分析工具

---

## 🚨 API Key 泄露后的应对

### 立即行动

1. **删除泄露的 API Key**
   - 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - 删除旧的 API Key

2. **生成新的 API Key**
   - 创建新的 API Key
   - 更新 Streamlit Cloud Secrets

3. **清理 Git 历史**（如果已提交到 GitHub）
   ```bash
   # 删除包含敏感信息的文件
   git rm SENSITIVE_FILE.md
   git commit -m "Remove sensitive file"
   
   # 从历史中移除
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch SENSITIVE_FILE.md" \
     --prune-empty --tag-name-filter cat -- --all
   
   # 强制推送
   git push origin --force --all
   ```

4. **监控异常活动**
   - 检查 API 使用统计
   - 查看是否有异常调用

---

## 🛡️ 额外的安全措施

### 1. 使用 API Key 限制功能

在 [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 中：
- 限制 API Key 只能访问特定的 API
- 限制 IP 地址（如果可能）
- 设置使用配额

### 2. 启用 GitHub Secret Scanning

GitHub 会自动扫描仓库中的敏感信息并发出警告。

### 3. 使用 `.gitignore`

确保以下文件被排除：
```
.env
.streamlit/secrets.toml
*.key
*.pem
config/secrets.yaml
```

### 4. 代码审查

- 提交前检查代码
- 使用 `git diff` 查看更改
- 团队协作时进行 Code Review

---

## 📋 安全检查清单

在每次部署前，检查以下项目：

- [ ] 代码中没有硬编码的 API Keys
- [ ] `.env` 文件已被 `.gitignore` 排除
- [ ] 文档中只使用占位符
- [ ] Streamlit Secrets 已正确配置
- [ ] Git 历史中没有敏感信息
- [ ] API Key 有适当的使用限制

---

## 🔗 相关资源

- [Google AI Studio](https://aistudio.google.com/)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

**记住：安全是持续的过程，而不是一次性的任务！** 🔒
