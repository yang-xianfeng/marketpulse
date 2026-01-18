# MarketPulse 开发指南

## 项目架构

### 分层设计

```
┌─────────────────────────────────────┐
│       应用层 (src/app.py)            │
│     MarketPulse 主应用程序           │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  分析层 (src/analyzer.py)            │
│   StockAnalyzer 股票分析器            │
│   StockAnalyzerFactory 工厂模式      │
└─────────────────────────────────────┘
      ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   数据层      │ │   策略层      │ │  通知层      │
│ providers.py │ │ strategies.py │ │ notifier.py │
└──────────────┘ └──────────────┘ └──────────────┘
      ↓              ↓              ↓
┌─────────────────────────────────────┐
│  基础设施层                           │
│  config.py (配置管理)                │
│  logger.py (日志系统)               │
└─────────────────────────────────────┘
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `app.py` | 应用入口，协调各个模块 |
| `analyzer.py` | 股票分析逻辑，调用策略和数据源 |
| `strategies.py` | 分析策略的抽象和实现 |
| `providers.py` | 数据获取，支持多源和故障转移 |
| `notifier.py` | 通知发送（邮件、钉钉等） |
| `config.py` | 配置文件和环境变量管理 |
| `logger.py` | 日志配置和初始化 |

## 核心概念

### 1. 数据提供者（DataProvider）

提供者模式，支持多个数据源：

```python
# 抽象基类
class DataProvider(ABC):
    def fetch(self, stock_code: str) -> pd.DataFrame:
        pass

# 实现类
class AkshareProvider(DataProvider): ...
class MockProvider(DataProvider): ...
class FallbackProvider(DataProvider):  # 故障转移
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback
```

**添加新数据源：**

```python
class MyCustomProvider(DataProvider):
    def fetch(self, stock_code: str) -> pd.DataFrame:
        # 实现数据获取逻辑
        return data
```

### 2. 策略（Strategy）

策略工厂模式，易于扩展：

```python
# 抽象基类
class Strategy(ABC):
    def analyze(self, data: pd.DataFrame) -> Optional[List[str]]:
        pass

# 具体实现
class MovingAverageStrategy(Strategy): ...

# 工厂注册
StrategyFactory.register("custom_strategy", CustomStrategy)
```

**添加新策略：**

```python
class MyStrategy(Strategy):
    def __init__(self, config: Dict = None):
        super().__init__("my_strategy", config)
    
    def analyze(self, data: pd.DataFrame) -> Optional[List[str]]:
        # 分析逻辑
        signals = []
        # ... 计算信号
        return signals if signals else None

# 在 config.json 中使用
{
  "strategies": [
    {
      "name": "my_strategy",
      "enabled": true,
      "type": "my_strategy",
      "params": { ... }
    }
  ]
}
```

### 3. 配置管理（ConfigManager）

支持环境变量替换：

```python
config = ConfigManager("config.json")

# 获取配置值（支持点表示法）
stocks = config.get_stocks()
email_config = config.get_email_config()
```

**环境变量替换：**

```json
{
  "email": {
    "sender": "${SENDER_EMAIL}",
    "receiver": "${RECEIVER_EMAIL}",
    "auth_code_env": "SMTP_AUTH_CODE"
  }
}
```

## 常见扩展场景

### 场景 1：添加新的技术指标策略

假设要添加 MACD 策略：

```python
# src/strategies.py 中添加

class MACDStrategy(Strategy):
    """MACD 策略"""
    
    def __init__(self, config: Dict = None):
        super().__init__("macd", config)
        self.fast_period = self.config.get("params", {}).get("fast_period", 12)
        self.slow_period = self.config.get("params", {}).get("slow_period", 26)
        self.signal_period = self.config.get("params", {}).get("signal_period", 9)
    
    def analyze(self, data: pd.DataFrame) -> Optional[List[str]]:
        if "close" not in data.columns:
            return None
        
        close = data["close"]
        
        # 计算 EMA
        ema_fast = close.ewm(span=self.fast_period).mean()
        ema_slow = close.ewm(span=self.slow_period).mean()
        
        # 计算 MACD 和信号线
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal_period).mean()
        
        # 检查最新的信号
        latest_macd = macd.iloc[-1]
        latest_signal = signal.iloc[-1]
        
        signals = []
        if pd.notna(latest_macd) and pd.notna(latest_signal):
            if latest_macd > latest_signal:
                signals.append("MACD 金叉 - 看涨")
            elif latest_macd < latest_signal:
                signals.append("MACD 死叉 - 看跌")
        
        return signals if signals else None

# 注册策略
StrategyFactory.register("macd", MACDStrategy)
```

然后在 `config.json` 中添加：

```json
{
  "strategies": [
    {
      "name": "macd",
      "enabled": true,
      "type": "macd",
      "params": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      }
    }
  ]
}
```

### 场景 2：添加钉钉通知

```python
# src/notifier.py 中添加

import requests

class DingTalkNotifier:
    """钉钉通知器"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, title: str, content: str) -> bool:
        """发送钉钉消息"""
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n{content}"
                }
            }
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"钉钉通知失败: {e}")
            return False

# 在 Notifier 类中集成

class Notifier:
    def __init__(self, notification_config: Dict = None):
        # ... 现有代码 ...
        
        self.dingtalk_notifier = None
        if notification_config.get("dingtalk", {}).get("enabled"):
            webhook_url = notification_config.get("dingtalk", {}).get("webhook_url")
            self.dingtalk_notifier = DingTalkNotifier(webhook_url)
    
    def notify(self, subject: str, body: str) -> bool:
        success = True
        
        # 邮件通知
        if self.email_notifier:
            if not self.email_notifier.send(subject, body):
                success = False
        
        # 钉钉通知
        if self.dingtalk_notifier:
            if not self.dingtalk_notifier.send(subject, body):
                success = False
        
        return success
```

在 `config.json` 中配置：

```json
{
  "notification": {
    "dingtalk": {
      "enabled": true,
      "webhook_url": "${DINGTALK_WEBHOOK}"
    }
  }
}
```

### 场景 3：添加数据缓存

```python
# src/providers.py 中添加

from functools import lru_cache
from datetime import datetime, timedelta

class CachedProvider(DataProvider):
    """带缓存的数据提供者"""
    
    def __init__(self, provider: DataProvider, ttl_minutes: int = 60):
        self.provider = provider
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache = {}
    
    def fetch(self, stock_code: str) -> Optional[pd.DataFrame]:
        # 检查缓存
        if stock_code in self.cache:
            cached_data, cached_time = self.cache[stock_code]
            if datetime.now() - cached_time < self.ttl:
                logger.info(f"使用缓存数据: {stock_code}")
                return cached_data
        
        # 获取新数据
        data = self.provider.fetch(stock_code)
        if data is not None:
            self.cache[stock_code] = (data, datetime.now())
        
        return data
```

## 测试

### 单元测试示例

```python
import unittest
from src.strategies import MovingAverageStrategy
import pandas as pd
import numpy as np

class TestMovingAverageStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MovingAverageStrategy({
            "params": {
                "periods": [5, 10, 20],
                "signals": {
                    "break_ma5": "跌破5日线",
                    "break_ma10": "跌破10日线",
                    "break_ma20": "跌破20日线"
                }
            }
        })
    
    def test_analyze_triggers_signal(self):
        # 生成测试数据
        data = pd.DataFrame({
            "close": [10, 10.1, 10.2, 10.3, 9.8, 9.5, 9.2, 9.0, 8.8, 8.5,
                      8.3, 8.1, 7.9, 7.8, 7.7, 7.6, 7.5, 7.4, 7.3, 7.2]
        })
        
        signals = self.strategy.analyze(data)
        self.assertIsNotNone(signals)
        self.assertTrue(len(signals) > 0)
```

## 性能优化

### 1. 并发数据获取

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_batch_concurrent(self, stock_codes: List[str]) -> List[Dict]:
    results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(self.analyze, code): code 
                   for code in stock_codes}
        
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
    
    return results
```

### 2. 数据预加载和缓存

```python
# 在 config.json 中启用缓存
{
  "data_source": {
    "cache_enabled": true,
    "cache_ttl_minutes": 60
  }
}
```

## 最佳实践

✅ 使用工厂模式实现可扩展的策略和提供者
✅ 在配置中定义参数，避免硬编码
✅ 完善的错误处理和日志记录
✅ 使用类型提示和 docstring
✅ 编写单元测试
✅ 定期更新依赖和安全补丁

## 故障排查

### 导入错误

确保在模块中导入正确：

```python
# ❌ 不要这样
from src.strategies import MovingAverageStrategy

# ✅ 应该这样（相对导入）
from .strategies import MovingAverageStrategy
```

### 配置值为 None

检查 `.env` 文件是否正确设置：

```bash
source .env
echo $SENDER_EMAIL
```

### 数据格式不一致

在新增数据提供者时，始终标准化输出格式：

```python
def _standardize_columns(data: pd.DataFrame) -> pd.DataFrame:
    # 确保包含 'date' 和 'close' 列
    required_columns = ['date', 'close']
    return data[required_columns]
```

## 参考资源

- [pandas 文档](https://pandas.pydata.org/docs/)
- [akshare 文档](https://github.com/akshare/akshare)
- [Python 设计模式](https://refactoring.guru/design-patterns/python)
