#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""策略模块"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class Strategy(ABC):
    """策略基类"""

    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Optional[List[str]]:
        """
        分析股票数据

        Args:
            data: 包含 'close' 列的 DataFrame

        Returns:
            触发的信号列表，如果无信号返回 None
        """
        pass


class MovingAverageStrategy(Strategy):
    """移动平均线策略"""

    def __init__(self, config: Dict = None):
        super().__init__("moving_average", config)
        self.periods = self.config.get("params", {}).get("periods", [5, 10, 20])
        self.signals_config = self.config.get("params", {}).get("signals", {})

    def analyze(self, data: pd.DataFrame) -> Optional[List[str]]:
        """分析股票，返回触发的信号"""
        if data is None or len(data) < max(self.periods):
            return None

        if "close" not in data.columns:
            logger.error("数据缺少 'close' 列")
            return None

        # 计算移动平均线
        close_prices = data["close"]

        for period in self.periods:
            data[f"MA{period}"] = close_prices.rolling(window=period).mean()

        # 获取最新数据
        latest = data.iloc[-1]
        latest_price = latest["close"]

        signals = []

        # 检查是否跌破各均线
        if pd.notna(latest.get("MA5")) and latest_price < latest["MA5"]:
            signal_msg = self.signals_config.get(
                "break_ma5", f"价格 ({latest_price:.2f}) 已跌破5日均线 ({latest['MA5']:.2f})"
            )
            signals.append(signal_msg)

        if pd.notna(latest.get("MA10")) and latest_price < latest["MA10"]:
            signal_msg = self.signals_config.get(
                "break_ma10", f"价格 ({latest_price:.2f}) 已跌破10日均线 ({latest['MA10']:.2f})"
            )
            signals.append(signal_msg)

        if pd.notna(latest.get("MA20")) and latest_price < latest["MA20"]:
            signal_msg = self.signals_config.get(
                "break_ma20", f"价格 ({latest_price:.2f}) 已跌破20日均线 ({latest['MA20']:.2f})"
            )
            signals.append(signal_msg)

        return signals if signals else None


class StrategyFactory:
    """策略工厂"""

    _strategies = {"moving_average": MovingAverageStrategy}

    @classmethod
    def create(cls, name: str, config: Dict = None) -> Optional[Strategy]:
        """创建策略实例"""
        strategy_class = cls._strategies.get(name)
        if strategy_class is None:
            logger.warning(f"未知的策略: {name}")
            return None

        return strategy_class(config)

    @classmethod
    def register(cls, name: str, strategy_class):
        """注册新策略"""
        cls._strategies[name] = strategy_class
