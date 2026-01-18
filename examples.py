#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarketPulse 使用示例
展示如何使用 MarketPulse 进行股票分析和策略扩展
"""

from src.config import ConfigManager
from src.providers import AkshareProvider, MockProvider, FallbackProvider
from src.analyzer import StockAnalyzer
from src.strategies import StrategyFactory, Strategy
from src.notifier import Notifier
import pandas as pd


def example_1_basic_usage():
    """例 1：基础使用 - 直接运行分析"""
    print("=" * 60)
    print("例 1：基础使用")
    print("=" * 60)

    from src.app import MarketPulse

    app = MarketPulse(config_file="config.json")
    result = app.run()

    print(f"\n分析结果: {result['triggered']} 只股票触发策略")
    print()


def example_2_custom_data_provider():
    """例 2：使用自定义数据提供者"""
    print("=" * 60)
    print("例 2：自定义数据提供者")
    print("=" * 60)

    # 使用模拟数据提供者
    provider = MockProvider()
    data = provider.fetch("002738")

    print(f"获取的数据形状: {data.shape}")
    print(f"数据列: {data.columns.tolist()}")
    print(f"前 5 行数据:\n{data.head()}")
    print()


def example_3_custom_strategy():
    """例 3：创建和注册自定义策略"""
    print("=" * 60)
    print("例 3：创建自定义策略")
    print("=" * 60)

    class RSIStrategy(Strategy):
        """RSI 相对强弱指数策略示例"""

        def __init__(self, config=None):
            super().__init__("rsi", config)

        def analyze(self, data: pd.DataFrame):
            """简化的 RSI 分析示例"""
            if len(data) < 14:
                return None

            # 计算价格变化
            delta = data["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            latest_rsi = rsi.iloc[-1]

            signals = []
            if latest_rsi < 30:
                signals.append(f"RSI 低于 30 ({latest_rsi:.2f}) - 超卖信号")
            elif latest_rsi > 70:
                signals.append(f"RSI 高于 70 ({latest_rsi:.2f}) - 超买信号")

            return signals if signals else None

    # 注册策略
    StrategyFactory.register("rsi", RSIStrategy)

    print("RSI 策略已注册")
    print(f"可用策略: {StrategyFactory._strategies.keys()}")
    print()


def example_4_config_management():
    """例 4：配置管理"""
    print("=" * 60)
    print("例 4：配置管理")
    print("=" * 60)

    config = ConfigManager("config.json")

    print(f"监控股票: {config.get_stocks()}")
    print(f"邮件配置: {config.get('notification.email.enabled')}")
    print(f"数据源: {config.get('data_source.primary')}")
    print(f"策略列表: {[s.get('name') for s in config.get_strategies()]}")
    print()


def example_5_batch_analysis():
    """例 5：批量分析"""
    print("=" * 60)
    print("例 5：批量分析")
    print("=" * 60)

    provider = FallbackProvider(AkshareProvider(), MockProvider())
    config = ConfigManager("config.json")
    strategies = config.get_strategies()

    analyzer = StockAnalyzer(provider, strategies)

    stocks = ["002738", "159545"]
    results = analyzer.analyze_batch(stocks)

    print(f"分析了 {len(stocks)} 只股票，{len(results)} 只触发策略")
    for result in results:
        print(f"  - {result['code']}: {len(result['signals'])} 个信号")
    print()


def example_6_notification():
    """例 6：发送通知"""
    print("=" * 60)
    print("例 6：发送通知")
    print("=" * 60)

    config = ConfigManager("config.json")
    notifier = Notifier(config.get("notification", {}))

    # 发送测试通知
    subject = "【MarketPulse】测试通知"
    body = """
测试邮件正文

如果看到这条消息，说明邮件配置正确。

---
MarketPulse
"""

    result = notifier.notify(subject, body)
    print(f"通知发送结果: {'成功' if result else '失败（可能是因为配置不完整）'}")
    print()


if __name__ == "__main__":
    # 运行所有示例
    example_1_basic_usage()
    example_2_custom_data_provider()
    example_3_custom_strategy()
    example_4_config_management()
    example_5_batch_analysis()
    example_6_notification()

    print("=" * 60)
    print("所有示例执行完成")
    print("=" * 60)
