#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""股票分析器模块"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from .providers import DataProvider, FallbackProvider, AkshareProvider, MockProvider
from .strategies import StrategyFactory

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """股票分析器"""

    def __init__(self, data_provider: DataProvider, strategies: List[Dict] = None):
        """
        初始化分析器

        Args:
            data_provider: 数据提供者
            strategies: 策略配置列表
        """
        self.data_provider = data_provider
        self.strategies = []

        # 初始化策略
        if strategies:
            for strategy_config in strategies:
                if strategy_config.get("enabled", True):
                    strategy = StrategyFactory.create(
                        strategy_config.get("type"), strategy_config
                    )
                    if strategy:
                        self.strategies.append(strategy)

    def analyze(self, stock_code: str) -> Optional[Dict]:
        """
        分析单只股票

        Args:
            stock_code: 股票代码

        Returns:
            分析结果字典或 None
        """
        try:
            logger.info(f"分析股票 {stock_code}")

            # 获取数据
            data = self.data_provider.fetch(stock_code)

            if data is None or len(data) == 0:
                logger.warning(f"无法获取 {stock_code} 的数据")
                return None

            # 执行所有策略
            all_signals = []
            for strategy in self.strategies:
                signals = strategy.analyze(data.copy())
                if signals:
                    all_signals.extend(signals)

            if not all_signals:
                logger.info(f"股票 {stock_code} 无触发信号")
                return None

            # 构造结果
            latest = data.iloc[-1]
            latest_date = latest.get("date", datetime.now())
            latest_price = latest.get("close", 0)

            return {
                "code": stock_code,
                "date": str(latest_date),
                "price": float(latest_price),
                "signals": all_signals,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"分析股票 {stock_code} 时出错: {e}", exc_info=True)
            return None

    def analyze_batch(self, stock_codes: List[str]) -> List[Dict]:
        """
        批量分析股票

        Args:
            stock_codes: 股票代码列表

        Returns:
            分析结果列表
        """
        results = []

        for stock_code in stock_codes:
            result = self.analyze(stock_code)
            if result:
                results.append(result)

        return results


class StockAnalyzerFactory:
    """股票分析器工厂"""

    @staticmethod
    def create(config: Dict) -> StockAnalyzer:
        """
        从配置创建分析器

        Args:
            config: 配置对象（需要有 get_data_source、get_strategies 方法）

        Returns:
            股票分析器实例
        """
        # 创建数据提供者
        data_source = config.get_data_source()

        if data_source.get("primary") == "akshare":
            primary = AkshareProvider()
            fallback = MockProvider()
            provider = FallbackProvider(primary, fallback)
        else:
            provider = MockProvider()

        # 创建分析器
        strategies = config.get_strategies()
        analyzer = StockAnalyzer(provider, strategies)

        return analyzer
