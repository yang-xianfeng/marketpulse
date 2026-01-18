#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MarketPulse 主应用模块"""

import logging
from datetime import datetime
from typing import List, Dict

from .analyzer import StockAnalyzerFactory
from .config import ConfigManager
from .logger import setup_logger
from .notifier import Notifier

logger = logging.getLogger(__name__)


class MarketPulse:
    """MarketPulse 主应用"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化应用

        Args:
            config_file: 配置文件路径
        """
        # 加载配置
        self.config = ConfigManager(config_file)

        # 配置日志
        log_config = self.config.get_logging_config()
        setup_logger(
            name="",
            level=log_config.get("level", "INFO"),
            log_file=log_config.get("file"),
            format_str=log_config.get("format"),
        )

        # 初始化分析器和通知器
        self.analyzer = StockAnalyzerFactory.create(self.config)
        notification_config = self.config.get("notification", {})
        self.notifier = Notifier(notification_config)

    def run(self) -> Dict:
        """
        运行分析和通知

        Returns:
            执行结果统计
        """
        stocks = self.config.get_stocks()

        if not stocks:
            logger.warning("未配置监控股票")
            return {"total": 0, "triggered": 0, "results": []}

        logger.info(f"开始分析 {len(stocks)} 只股票: {stocks}")

        # 分析股票
        results = self.analyzer.analyze_batch(stocks)

        # 发送通知
        triggered_count = 0
        for result in results:
            triggered_count += 1
            self._notify(result)

        # 日志汇总
        self._log_summary(stocks, results)

        return {
            "total": len(stocks),
            "triggered": triggered_count,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def _notify(self, result: Dict) -> None:
        """发送单只股票的通知"""
        try:
            subject = f"【MarketPulse】股票策略触发: {result['code']}"

            # 构造邮件正文
            body = f"""股票代码: {result['code']}
交易日期: {result['date']}
当前价格: {result['price']:.2f}

触发信号:
"""

            for signal in result["signals"]:
                body += f"  • {signal}\n"

            body += f"""
---
MarketPulse - Daily Beat
https://github.com/yang-xianfeng/marketpulse
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            logger.info(f"发送通知: {subject}")
            self.notifier.notify(subject, body)

        except Exception as e:
            logger.error(f"发送通知失败: {e}", exc_info=True)

    @staticmethod
    def _log_summary(stocks: List[str], results: List[Dict]) -> None:
        """记录汇总信息"""
        logger.info(f"\n{'='*60}")
        logger.info(f"分析完成")
        logger.info(f"  监控股票数: {len(stocks)}")
        logger.info(f"  触发股票数: {len(results)}")

        if results:
            logger.info("  触发详情:")
            for result in results:
                logger.info(
                    f"    - {result['code']}: 日期 {result['date']}, 价格 {result['price']:.2f}"
                )

        logger.info(f"{'='*60}\n")


def main(config_file: str = "config.json"):
    """主入口"""
    try:
        app = MarketPulse(config_file)
        result = app.run()
        return result
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
