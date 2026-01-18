# MarketPulse - 快速参考卡

## 常用命令

```bash
# 安装和运行
pip install -r requirements.txt
python main.py

# 环境配置
cp .env.example .env
nano .env  # 或使用你的编辑器

# 验证项目
python verify_project.py

# 查看日志
tail -f marketpulse.log

# 运行示例
python examples.py
```

## 配置修改

### 修改监控股票

编辑 `config.json`：

```json
{
  "stocks": {
    "watchlist": ["002738", "159545", "159915"]
  }
}
```

### 修改均线周期

编辑 `config.json`：

```json
{
  "strategies": [
    {
      "params": {
        "periods": [5, 10, 20]  // 修改这里
      }
    }
  ]
}
```

### 修改邮箱配置

编辑 `.env`：

```bash
SENDER_EMAIL=your_email@qq.com
RECEIVER_EMAIL=receiver@qq.com
SMTP_AUTH_CODE=your_16_digit_code
```

## 常见问题速查

| 问题 | 解决方案 |
|------|--------|
| 程序找不到 config.json | 确保在项目根目录运行 |
| 邮件没有发送 | 检查 .env 中的邮箱和授权码 |
| 数据获取失败 | 检查网络，akshare 会自动转用模拟数据 |
| Python 版本问题 | 需要 Python 3.10+ |
| 导入错误 | 运行 `pip install -r requirements.txt` |

## 模块导入速查

```python
# 主应用
from src.app import MarketPulse

# 配置管理
from src.config import ConfigManager

# 数据提供者
from src.providers import AkshareProvider, MockProvider, FallbackProvider

# 策略
from src.strategies import StrategyFactory, MovingAverageStrategy

# 分析器
from src.analyzer import StockAnalyzer

# 通知器
from src.notifier import Notifier

# 日志
from src.logger import setup_logger, get_logger
```

## 快速代码片段

### 快速分析一只股票

```python
from src.providers import MockProvider
from src.analyzer import StockAnalyzer
from src.config import ConfigManager

config = ConfigManager("config.json")
provider = MockProvider()
analyzer = StockAnalyzer(provider, config.get_strategies())

result = analyzer.analyze("002738")
if result:
    print(f"触发信号: {result['signals']}")
else:
    print("无触发信号")
```

### 注册新策略

```python
from src.strategies import Strategy, StrategyFactory

class MyStrategy(Strategy):
    def analyze(self, data):
        # 实现分析逻辑
        return ["信号 1", "信号 2"]

StrategyFactory.register("my_strategy", MyStrategy)
```

### 发送测试邮件

```python
from src.config import ConfigManager
from src.notifier import Notifier

config = ConfigManager("config.json")
notifier = Notifier(config.get("notification"))

notifier.notify("测试", "这是测试邮件")
```

## 文件快速导航

| 文件 | 用途 | 何时修改 |
|------|------|--------|
| config.json | 配置 | 修改股票、策略参数 |
| .env | 邮箱配置 | 第一次运行时 |
| src/app.py | 主应用逻辑 | 需要修改工作流 |
| src/strategies.py | 策略 | 添加新策略 |
| src/providers.py | 数据源 | 添加新数据源 |
| src/notifier.py | 通知 | 添加新通知方式 |

## 日志级别说明

```json
{
  "logging": {
    "level": "DEBUG"    // DEBUG, INFO, WARNING, ERROR
  }
}
```

| 级别 | 说明 | 使用场景 |
|------|------|--------|
| DEBUG | 最详细，包含所有信息 | 开发和调试 |
| INFO | 一般信息 | **推荐用于生产** |
| WARNING | 警告信息 | 配置不完整等 |
| ERROR | 错误信息 | 程序遇到问题 |

## GitHub Actions 快速参考

### 获取执行日志

1. 打开 GitHub 仓库
2. 点击 **Actions**
3. 选择 **Daily Analysis**
4. 点击最近的运行记录
5. 查看 **Run MarketPulse analysis** 步骤

### 手动触发工作流

1. 打开 GitHub 仓库
2. 点击 **Actions**
3. 选择 **Daily Analysis**
4. 点击 **Run workflow**
5. 选择分支并运行

### 设置 GitHub Secrets

1. 进入 **Settings → Secrets and variables → Actions**
2. 点击 **New repository secret**
3. 添加：
   - `SENDER_EMAIL`
   - `RECEIVER_EMAIL`
   - `SMTP_AUTH_CODE`

## 性能调优

### 加快数据获取

```json
{
  "data_source": {
    "cache_enabled": true,
    "cache_ttl_minutes": 60
  }
}
```

### 减少分析时间

- 减少 `periods` 的数量
- 减少监控的股票数量
- 使用 MockProvider 代替 AkshareProvider

## 常用环境变量

```bash
# 必需
SENDER_EMAIL
RECEIVER_EMAIL
SMTP_AUTH_CODE

# 可选
LOG_LEVEL=INFO              # 日志级别
PYTHONUNBUFFERED=1          # 实时输出日志
```

## 回滚命令

如果出现问题需要恢复：

```bash
# 恢复默认配置
git checkout config.json

# 清除缓存和日志
rm -f marketpulse.log __pycache__ .pytest_cache

# 重新安装依赖
pip install --upgrade -r requirements.txt
```

## 性能指标基准

```
3 只股票分析：~30 秒
- 数据获取：~15 秒
- 分析：~1 秒
- 邮件：~2 秒
- 其他：~12 秒

内存占用：~50 MB
CPU 使用：~5%
```

## 📚 文档速查

- 🏠 [项目总览](PROJECT_OVERVIEW.md)
- 📖 [完整文档](README.md)
- ⚡ [快速开始](QUICKSTART.md)
- 🔨 [开发指南](DEVELOPMENT.md)
- 🔒 [安全说明](SECURITY.md)
- 🚀 [部署清单](DEPLOYMENT.md)
- 📋 [变更记录](CHANGELOG.md)

---

**版本**：v1.0.0
**最后更新**：2026-01-18
