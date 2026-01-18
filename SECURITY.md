# MarketPulse 安全性说明

## 敏感信息处理

本项目采用以下安全措施保护邮箱和秘钥：

### 1. 环境变量存储

所有敏感信息（邮箱地址、授权码）存储在环境变量中，而非配置文件：

```bash
SENDER_EMAIL=your_email@qq.com
RECEIVER_EMAIL=receiver@qq.com
SMTP_AUTH_CODE=your_16_digit_auth_code
```

### 2. .gitignore 保护

`.env` 文件已添加到 `.gitignore`，确保本地环境文件不会被提交到 Git 仓库。

### 3. GitHub Actions Secrets

在 GitHub Actions 中使用 Secrets 存储敏感信息：

```yaml
env:
  SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
  RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
  SMTP_AUTH_CODE: ${{ secrets.SMTP_AUTH_CODE }}
```

### 4. 配置文件中的占位符

`config.json` 中使用 `${VARIABLE_NAME}` 形式的占位符：

```json
{
  "email": {
    "sender": "${SENDER_EMAIL}",
    "receiver": "${RECEIVER_EMAIL}",
    "auth_code_env": "SMTP_AUTH_CODE"
  }
}
```

运行时自动从环境变量替换。

## 配置流程

### 本地开发

1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 填入真实的邮箱信息
3. `.env` 文件会被 Git 自动忽略

### GitHub Actions 部署

1. 在 GitHub 仓库设置中添加 Secrets：
   - Settings → Secrets → New repository secret
   - 添加 SENDER_EMAIL、RECEIVER_EMAIL、SMTP_AUTH_CODE

2. 工作流文件引用这些 Secrets

## 最佳实践

✅ 使用 QQ 邮箱专用授权码，不要使用真实密码
✅ 定期更新授权码
✅ 不要在代码、日志中打印敏感信息
✅ 定期审查 `.gitignore` 确保敏感文件被忽略
✅ 在 GitHub Actions 中使用 Secrets，不要硬编码
✅ 使用唯一的专用邮箱账号进行通知

## 故障排查

### 环境变量未被读取

确保在运行程序前导出环境变量：

```bash
export SENDER_EMAIL="..."
export RECEIVER_EMAIL="..."
export SMTP_AUTH_CODE="..."
python main.py
```

或使用 `.env` 文件配合 python-dotenv：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 邮件发送时显示未配置

检查环境变量是否正确设置：

```bash
echo $SENDER_EMAIL
echo $RECEIVER_EMAIL
echo $SMTP_AUTH_CODE
```
