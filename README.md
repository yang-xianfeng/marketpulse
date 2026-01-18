# MarketPulse - 股票策略监控系统

一个简洁、健壮、可扩展的股票策略监控系统，支持多种策略和数据源。

## 核心特性

- **模块化设计**：清晰的架构，易于扩展新策略
- **安全配置**：邮箱授权码从环境变量读取，避免敏感信息泄露
- **故障转移**：主数据源失败自动使用备用源
- **灵活策略**：支持多种策略，通过配置文件定义
- **持久化配置**：股票库、通知时间、接收邮件等均可配置

## 目录结构

```
marketpulse/
├── src/                      # 源代码包
│   ├── __init__.py
│   ├── app.py               # 主应用程序
│   ├── config.py            # 配置管理
│   ├── logger.py            # 日志配置
│   ├── providers.py         # 数据提供者（支持故障转移）
│   ├── strategies.py        # 策略基类和实现
│   ├── analyzer.py          # 股票分析器
│   └── notifier.py          # 邮件和通知器
├── main.py                  # 程序入口
├── config.json              # 配置文件
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
└── README.md               # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env，填入你的邮箱信息
# SENDER_EMAIL=your_email@qq.com
# RECEIVER_EMAIL=receiver@qq.com
# SMTP_AUTH_CODE=your_16_digit_auth_code
```

### 3. 编辑 config.json

修改监控的股票列表和其他配置：

```json
{
  "stocks": {
    "watchlist": ["002738", "159545", "159915"]
  }
}
```

### 4. 运行程序

```bash
python main.py
```

## 配置说明

### config.json 结构

```json
{
  "stocks": {
    "watchlist": ["002738", "159545", "159915"],
    "description": "自选股票库"
  },
  "notification": {
    "enabled": true,
    "email": {
      "enabled": true,
      "sender": "${SENDER_EMAIL}",
      "receiver": "${RECEIVER_EMAIL}",
      "smtp_server": "smtp.qq.com",
      "smtp_port": 465,
      "auth_code_env": "SMTP_AUTH_CODE"
    }
  },
  "strategies": [
    {
      "name": "ma_crossover",
      "enabled": true,
      "type": "moving_average",
      "params": {
        "periods": [5, 10, 20]
      }
    }
  ],
  "data_source": {
    "primary": "akshare",
    "fallback": "mock"
  },
  "logging": {
    "level": "INFO",
    "file": "marketpulse.log"
  }
}
```

## 关键模块说明

### 数据提供者（providers.py）

- **AkshareProvider**：从 akshare 获取实时行情
- **MockProvider**：生成模拟数据（用于测试）
- **FallbackProvider**：主源失败自动切换到备用源

### 策略系统（strategies.py）

支持工厂模式扩展：

```python
from src.strategies import StrategyFactory

# 注册自定义策略
class MyStrategy(Strategy):
    def analyze(self, data):
        # 实现分析逻辑
        pass

StrategyFactory.register("my_strategy", MyStrategy)
```

### 分析器（analyzer.py）

支持批量分析和并行处理：

```python
analyzer = StockAnalyzer(provider, strategies)
results = analyzer.analyze_batch(stock_codes)
```

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| SENDER_EMAIL | 发件邮箱 | 2506266549@qq.com |
| RECEIVER_EMAIL | 收件邮箱 | 1152188090@qq.com |
| SMTP_AUTH_CODE | QQ 邮箱授权码 | 16 位授权码 |
| LOG_LEVEL | 日志级别 | INFO, DEBUG |

### 获取 QQ 邮箱授权码

1. 登录 QQ 邮箱
2. 进入设置 → 账户
3. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务"
4. 启用 "POP3/SMTP 服务"
5. 获取授权码（16 位）

## 安全性考虑

✅ **已实现的安全措施**

- 邮箱授权码从环境变量读取，不在配置文件中
- .env 文件已加入 .gitignore，不会提交到仓库
- 支持多种数据源，单一源故障不影响整体服务
- 完整的错误处理和日志记录

✅ **推荐做法**

- 定期更新依赖包
- 使用 QQ 邮箱专用授权码，不要使用真实密码
- 在 GitHub Actions 中使用 Secrets 存储敏感信息
- 定期审查日志文件

## 扩展指南

### 添加新的数据提供者

```python
from src.providers import DataProvider

class CustomProvider(DataProvider):
    def fetch(self, stock_code: str):
        # 实现数据获取逻辑
        return data

# 在 config.json 中指定使用
```

### 添加新的策略

```python
from src.strategies import Strategy, StrategyFactory

class CustomStrategy(Strategy):
    def analyze(self, data):
        # 实现策略逻辑
        return signals

# 注册策略
StrategyFactory.register("custom", CustomStrategy)
```

### 添加新的通知方式

```python
# 扩展 notifier.py 中的 Notifier 类
# 添加对钉钉、企业微信等的支持
```

## GitHub Actions 集成

使用以下工作流配置每日运行：

```yaml
name: MarketPulse Daily Analysis

on:
  schedule:
    - cron: '0 9 * * 1-5'  # 周一至周五 09:00 运行

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: |
          pip install -r requirements.txt
          python main.py
        env:
          SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
          RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
          SMTP_AUTH_CODE: ${{ secrets.SMTP_AUTH_CODE }}
```

## 故障排查

### 邮件发送失败

1. 检查 SMTP_AUTH_CODE 是否正确
2. 确保 QQ 邮箱已启用 POP3/SMTP 服务
3. 检查防火墙是否阻止了 465 端口

### 数据获取失败

1. 检查网络连接
2. 查看日志文件 marketpulse.log
3. akshare 可能需要更新，运行 `pip install --upgrade akshare`

### 策略不触发

1. 检查 config.json 中策略是否启用
2. 验证股票代码格式是否正确
3. 检查 periods 参数是否合理

## 许可证

MIT

## 作者

yang-xianfeng

## 更新日志

### v1.0.0 (2026-01-18)

- 完整的模块化架构
- 支持多策略和多数据源
- 安全的配置管理
- 完善的错误处理和日志
