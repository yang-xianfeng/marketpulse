# MarketPulse 部署检查清单

## 本地开发环境配置

- [ ] 克隆项目：`git clone https://github.com/yang-xianfeng/marketpulse.git`
- [ ] 进入目录：`cd marketpulse`
- [ ] 创建虚拟环境：`python -m venv venv`
- [ ] 激活虚拟环境：`source venv/bin/activate` (Linux/Mac) 或 `venv\Scripts\activate` (Windows)
- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 运行完整性检查：`python verify_project.py`

## 配置步骤

### 1. 环境变量配置

- [ ] 复制示例文件：`cp .env.example .env`
- [ ] 编辑 `.env` 文件：`vi .env` 或用文本编辑器打开
- [ ] 填入邮箱地址（SENDER_EMAIL）
- [ ] 填入接收邮箱（RECEIVER_EMAIL）
- [ ] 填入 QQ 邮箱授权码（SMTP_AUTH_CODE）
  - [ ] 已获取 QQ 邮箱授权码（见 [SECURITY.md](SECURITY.md)）
- [ ] 验证环境变量：`cat .env`

### 2. 股票库配置

- [ ] 编辑 `config.json`
- [ ] 修改 `stocks.watchlist` 数组，添加要监控的股票代码
- [ ] 示例：`["002738", "159545", "159915"]`

### 3. 策略配置（可选）

- [ ] 打开 `config.json`
- [ ] 在 `strategies` 中修改均线周期（periods）
- [ ] 调整通知信号文案（signals）

### 4. 通知配置（可选）

- [ ] 启用/禁用邮件通知：修改 `notification.enabled`
- [ ] 修改 SMTP 服务器地址（如不使用 QQ 邮箱）
- [ ] 修改 SMTP 端口号（如需要）

## 测试运行

- [ ] 本地测试：`python main.py`
  - [ ] 检查日志输出（INFO 级别）
  - [ ] 确保股票分析完成
  - [ ] 验证触发信号显示正确（如有）
- [ ] 查看日志文件：`tail marketpulse.log`
- [ ] 邮件测试（如配置了邮箱）：
  - [ ] 检查是否收到测试邮件
  - [ ] 验证邮件内容正确

## GitHub 部署

### 1. 仓库设置

- [ ] 已 fork 或创建了自己的仓库
- [ ] 仓库已关闭（如为私有项目）

### 2. Secrets 配置

- [ ] 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
- [ ] 添加以下 Secrets：
  - [ ] `SENDER_EMAIL`：发件人邮箱
  - [ ] `RECEIVER_EMAIL`：接收人邮箱
  - [ ] `SMTP_AUTH_CODE`：QQ 邮箱授权码

### 3. 工作流启用

- [ ] `.github/workflows/daily-analysis.yml` 已启用
- [ ] 调整定时任务：
  - [ ] 默认时间：周一至周五 UTC 1:30（北京时间 9:30）
  - [ ] 可在 `cron` 字段修改时间
- [ ] `.github/workflows/test.yml` 已启用

### 4. 验证工作流

- [ ] 手动触发工作流：Actions → Daily Analysis → Run workflow
- [ ] 查看执行日志
- [ ] 验证邮件是否发送成功
- [ ] 检查工作流执行时间

## 监控和维护

### 日常维护

- [ ] 定期检查 GitHub Actions 执行日志
- [ ] 若邮件未发送，检查错误日志
- [ ] 定期更新依赖：`pip install --upgrade -r requirements.txt`

### 定期更新

- [ ] 每月检查一次 akshare 是否有新版本
- [ ] 更新策略配置以适应市场变化
- [ ] 备份重要配置文件

### 问题排查

邮件未发送：
- [ ] 检查 SMTP_AUTH_CODE 是否正确
- [ ] 验证邮箱是否启用了 POP3/SMTP 服务
- [ ] 查看日志中的具体错误信息

数据获取失败：
- [ ] 检查网络连接
- [ ] 尝试更新 akshare：`pip install --upgrade akshare`
- [ ] 查看程序是否使用了备用数据源

## 安全检查

- [ ] `.gitignore` 包含 `.env` 文件
- [ ] 从不在代码中硬编码密钥
- [ ] 定期更新 Python 依赖
- [ ] 使用强密码和授权码
- [ ] 不要将 `.env` 文件提交到仓库
- [ ] 不要在日志文件中输出敏感信息

## 备份和恢复

- [ ] 备份 `config.json`
- [ ] 备份 `.env` 文件（仅本地）
- [ ] 定期备份运行日志
- [ ] 保存 GitHub Actions Secrets 的记录（仅本地）

## 性能监控

- [ ] 记录每次运行的执行时间
- [ ] 监控日志文件大小（每周 ~100KB）
- [ ] 验证内存使用是否正常（~50MB）
- [ ] 确保 CPU 使用率合理（~5%）

## 文档维护

- [ ] 更新 README.md 中的股票列表（如需要）
- [ ] 更新 CHANGELOG.md 记录重要变更
- [ ] 保持 DEVELOPMENT.md 的代码示例最新
- [ ] 更新 SECURITY.md 中的安全建议

## 上线清单

- [ ] 所有测试都已通过
- [ ] 代码已审查
- [ ] 文档已更新
- [ ] 配置已验证
- [ ] GitHub Actions 已配置
- [ ] Secrets 已设置
- [ ] 首次运行邮件已发送成功
- [ ] 日志记录正常工作

---

## 快速验证命令

```bash
# 验证环境
python verify_project.py

# 验证语法
python -m py_compile src/*.py main.py

# 运行程序
python main.py

# 查看日志
tail -f marketpulse.log

# 检查环境变量
echo $SENDER_EMAIL
echo $RECEIVER_EMAIL
echo $SMTP_AUTH_CODE
```

## 紧急回滚

如果遇到严重问题：

```bash
# 停止所有运行
# （GitHub Actions 会在计划时间自动执行）

# 恢复备份
cp config.json.backup config.json

# 查看错误日志
tail marketpulse.log

# 禁用工作流
# GitHub → Actions → Daily Analysis → Disable
```

---

**版本**：v1.0.0
**最后更新**：2026-01-18
**维护人**：yang-xianfeng
