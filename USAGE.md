# MarketPulse 使用指南

## 项目概述

MarketPulse 是一个自动化的股票监控系统，可以：
- 定时监控自选股票的价格走势
- 根据移动平均线策略自动触发交易信号
- 通过邮件实时通知用户

## 核心功能

### 1. 股票数据获取
支持多种数据源：
- **Akshare API**（主要源）：获取实时股票数据
- **故障转移**：当主源失效时自动切换到模拟数据

### 2. 技术分析
计算以下指标：
- 5日移动平均线（MA5）
- 10日移动平均线（MA10）
- 20日移动平均线（MA20）

### 3. 交易信号
触发条件：
- **减仓信号**：股价跌破5日均线
- **再减仓信号**：股价跌破10日均线
- **清仓信号**：股价跌破20日均线

### 4. 邮件通知
- 支持 QQ 邮箱、Gmail 等 SMTP 邮箱
- 包含详细的价格和技术指标信息
- 可配置的收发地址

## 安装与配置

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 配置邮箱（可选）

编辑 `email_config.json`：

```json
{
  "sender_email": "your_email@qq.com",
  "receiver_email": "receiver_email@qq.com",
  "password": "your_smtp_password",
  "smtp_server": "smtp.qq.com",
  "smtp_port": 465,
  "enabled": true
}
```

#### QQ 邮箱配置说明：

1. 打开 QQ 邮箱官网：https://mail.qq.com
2. 进入 **设置 → 账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务**
4. 点击 **开启** POP3/SMTP 服务
5. 验证身份后获得 **授权码**
6. 在 `email_config.json` 中：
   - `sender_email`: 你的 QQ 邮箱地址
   - `password`: 授权码（不是登录密码！）
   - `smtp_server`: `smtp.qq.com`
   - `smtp_port`: `465`
   - `enabled`: `true`

### 步骤 3: 配置自选股票

编辑 `stock_strategy.py` 中的 `main()` 函数：

```python
def main():
    stock_list = ['002738', '159545', '159915']  # 修改为你的自选股票代码
    # ...
```

### 步骤 4: 本地测试

```bash
python stock_strategy.py
```

## GitHub Actions 部署

### 步骤 1: 上传到 GitHub

```bash
git add .
git commit -m "初始化 MarketPulse 项目"
git push origin main
```

### 步骤 2: 配置 GitHub Secrets

在 GitHub 仓库设置中（Settings → Secrets and variables → Actions）添加：

1. **EMAIL_CONFIG** Secret：
   - 值为完整的 JSON 配置（带有敏感信息）
   
   ```json
   {"sender_email":"your@qq.com","receiver_email":"receiver@qq.com","password":"your_auth_code","smtp_server":"smtp.qq.com","smtp_port":465,"enabled":true}
   ```

### 步骤 3: 自动化运行

- 工作流配置在 `.github/workflows/stock_strategy.yml`
- 默认每个交易日 **下午 3 点 (北京时间)** 自动运行
- 也可以在 Actions 标签页手动触发

## 架构设计

### 类设计

```
StockDataProvider (基类)
├── AkshareProvider (Akshare 数据源)
│   └── 故障转移 → MockDataProvider
└── MockDataProvider (模拟数据，用于测试)

StockStrategyAnalyzer
└── 使用 StockDataProvider 获取数据
└── 计算移动平均线
└── 检查交易信号

EmailNotifier
└── 从 email_config.json 加载配置
└── 发送 SMTP 邮件

MarketPulse (主类)
├── 使用 StockStrategyAnalyzer 分析股票
├── 使用 EmailNotifier 发送通知
└── 协调整个流程
```

### 关键改进

1. **错误处理**：完整的 try-catch 机制和日志记录
2. **故障转移**：Akshare 失效时自动使用模拟数据
3. **配置管理**：外部化配置文件，安全存储敏感信息
4. **日志记录**：详细的操作日志便于调试
5. **灵活设计**：易于扩展数据源和通知方式
6. **类型提示**：使用类型注解提高代码可读性
7. **模块化**：清晰的职责分离

## 常见问题

### Q1: 邮件无法发送？

检查清单：
- [ ] 邮箱地址正确
- [ ] 使用了授权码而非密码
- [ ] 邮箱 SMTP 服务已启用
- [ ] 检查 `enabled` 是否为 `true`
- [ ] 查看日志信息

### Q2: 获取不到股票数据？

可能原因：
- Akshare API 故障（会自动使用模拟数据）
- 网络连接问题
- 股票代码格式错误

### Q3: 如何修改检查频率？

编辑 `.github/workflows/stock_strategy.yml` 中的 `cron` 表达式：

```yaml
- cron: '0 7 * * 1-5'  # 每周一至五 7:00 UTC (15:00 北京时间)
```

Cron 格式：`分 小时 日期 月份 周几`

### Q4: 如何添加其他通知方式？

创建 `Notifier` 的子类：

```python
class DingTalkNotifier(Notifier):
    def send(self, subject: str, body: str) -> bool:
        # 实现钉钉通知逻辑
        pass
```

## 性能考虑

- 单个股票分析时间：~2-5 秒
- 10 只股票完整分析：~20-50 秒
- 邮件发送：~2-3 秒

## 安全建议

1. **不要在代码中提交敏感信息**
2. 使用 GitHub Secrets 存储邮箱密码
3. 定期更新依赖包
4. 监控 GitHub Actions 日志以发现异常

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
