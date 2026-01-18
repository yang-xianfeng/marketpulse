#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据提供者模块"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """数据提供者基类"""

    @abstractmethod
    def fetch(self, stock_code: str) -> Optional[pd.DataFrame]:
        """
        获取股票数据

        Args:
            stock_code: 股票代码

        Returns:
            包含 'date' 和 'close' 列的 DataFrame，或 None
        """
        pass


class AkshareProvider(DataProvider):
    """使用 akshare 获取数据的提供者"""

    def fetch(self, stock_code: str) -> Optional[pd.DataFrame]:
        """从 akshare 获取股票数据"""
        try:
            import akshare as ak

            symbol = self._format_symbol(stock_code)
            logger.info(f"从 akshare 获取 {stock_code} 的数据")

            data = ak.stock_zh_a_daily(symbol=symbol)

            if data is None or len(data) == 0:
                return None

            # 数据清理和标准化
            data = self._standardize_columns(data)
            return data

        except Exception as e:
            logger.error(f"akshare 获取数据失败: {e}")
            return None

    @staticmethod
    def _format_symbol(stock_code: str) -> str:
        """格式化股票代码"""
        stock_code = stock_code.strip()

        if stock_code.startswith(("sh", "sz")):
            return stock_code

        # 基金或特殊代码
        if stock_code.startswith("1"):
            return f"sz{stock_code}"
        # 上证
        elif stock_code.startswith("6"):
            return f"sh{stock_code}"
        # 默认深证
        else:
            return f"sz{stock_code}"

    @staticmethod
    def _standardize_columns(data: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        column_mapping = {
            "trade_date": "date",
            "日期": "date",
            "close_price": "close",
            "收盘": "close",
            "open_price": "open",
            "开盘": "open",
            "high_price": "high",
            "最高": "high",
            "low_price": "low",
            "最低": "low",
        }

        for old_name, new_name in column_mapping.items():
            if old_name in data.columns:
                data = data.rename(columns={old_name: new_name})

        # 确保必要列存在
        if "date" not in data.columns:
            # 如果没有 date 列，使用索引或生成日期
            if isinstance(data.index, pd.DatetimeIndex):
                data = data.reset_index()
                data = data.rename(columns={"index": "date"})
            else:
                logger.warning("无法找到日期列")

        return data[["date", "close"]].dropna() if "close" in data.columns else data


class MockProvider(DataProvider):
    """模拟数据提供者（用于测试和故障转移）"""

    def fetch(self, stock_code: str) -> pd.DataFrame:
        """生成模拟数据"""
        logger.info(f"使用模拟数据生成 {stock_code} 的数据")

        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        np.random.seed(hash(stock_code) % (2**32))

        base_price = 10 + (hash(stock_code) % 100) / 10
        prices = base_price + np.cumsum(np.random.randn(60) * 0.5)

        return pd.DataFrame({"date": dates, "close": prices})


class FallbackProvider(DataProvider):
    """故障转移数据提供者"""

    def __init__(self, primary: DataProvider, fallback: DataProvider):
        self.primary = primary
        self.fallback = fallback

    def fetch(self, stock_code: str) -> Optional[pd.DataFrame]:
        """先尝试主数据源，失败则使用备用源"""
        data = self.primary.fetch(stock_code)

        if data is not None and not data.empty:
            return data

        logger.info(f"尝试使用备用提供者获取 {stock_code} 的数据")
        return self.fallback.fetch(stock_code)
