#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarketPulse 测试脚本
"""

import sys
import logging
from stock_strategy import (
    StockDataProvider,
    AkshareProvider,
    MockDataProvider,
    StockStrategyAnalyzer,
    EmailNotifier,
    MarketPulse
)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mock_data_provider():
    """测试模拟数据提供者"""
    logger.info("\n" + "="*60)
    logger.info("测试 1: 模拟数据提供者")
    logger.info("="*60)
    
    provider = MockDataProvider()
    data = provider.get_stock_data('002738')
    
    logger.info(f"✓ 成功获取模拟数据")
    logger.info(f"  数据形状: {data.shape}")
    logger.info(f"  列名: {data.columns.tolist()}")
    logger.info(f"  首行:\n{data.head(1)}")
    
    assert 'close' in data.columns, "缺少 'close' 列"
    assert len(data) > 0, "数据为空"
    
    return True


def test_strategy_analyzer():
    """测试策略分析器"""
    logger.info("\n" + "="*60)
    logger.info("测试 2: 策略分析器")
    logger.info("="*60)
    
    provider = MockDataProvider()
    analyzer = StockStrategyAnalyzer(provider)
    
    result = analyzer.analyze('002738')
    
    logger.info(f"✓ 分析完成")
    
    if result:
        logger.info(f"  触发股票: {result['code']}")
        logger.info(f"  交易日期: {result['date']}")
        logger.info(f"  当前价格: {result['price']:.2f}")
        logger.info(f"  信号:\n{result['signals']}")
    else:
        logger.info(f"  无触发信号")
    
    return True


def test_email_notifier():
    """测试邮件通知器"""
    logger.info("\n" + "="*60)
    logger.info("测试 3: 邮件通知器")
    logger.info("="*60)
    
    notifier = EmailNotifier('email_config.json')
    
    logger.info(f"✓ 邮件通知器初始化成功")
    logger.info(f"  发件人: {notifier.config.get('sender_email')}")
    logger.info(f"  收件人: {notifier.config.get('receiver_email')}")
    logger.info(f"  已启用: {notifier.config.get('enabled', False)}")
    
    # 测试邮件发送（禁用状态下只会记录日志）
    success = notifier.send(
        subject="[测试] MarketPulse 邮件通知测试",
        body="这是一条测试邮件。\n\n如果您收到此邮件，说明邮件配置正确。"
    )
    
    logger.info(f"✓ 邮件发送结果: {'成功' if success else '跳过（已禁用）'}")
    
    return True


def test_market_pulse_integration():
    """集成测试 MarketPulse"""
    logger.info("\n" + "="*60)
    logger.info("测试 4: MarketPulse 集成测试")
    logger.info("="*60)
    
    test_stocks = ['002738', '159545', '159915']
    
    market_pulse = MarketPulse(
        stock_list=test_stocks,
        data_provider=MockDataProvider(),
        notifier=EmailNotifier('email_config.json')
    )
    
    logger.info(f"✓ MarketPulse 初始化成功")
    logger.info(f"  监控股票数: {len(test_stocks)}")
    logger.info(f"  股票列表: {test_stocks}")
    
    try:
        market_pulse.run()
        logger.info(f"✓ 分析完成")
        return True
    except Exception as e:
        logger.error(f"✗ 分析失败: {e}", exc_info=True)
        return False


def test_akshare_with_fallback():
    """测试 Akshare 与故障转移"""
    logger.info("\n" + "="*60)
    logger.info("测试 5: Akshare 与故障转移")
    logger.info("="*60)
    
    # 创建带有故障转移的 Akshare 提供者
    provider = AkshareProvider(fallback_provider=MockDataProvider())
    
    logger.info(f"✓ Akshare 提供者初始化成功（带故障转移）")
    
    try:
        data = provider.get_stock_data('002738')
        logger.info(f"✓ 成功获取数据")
        logger.info(f"  数据形状: {data.shape}")
        logger.info(f"  列名: {data.columns.tolist()}")
        return True
    except Exception as e:
        logger.error(f"✗ 获取数据失败: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("\n\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*15 + "MarketPulse 系统测试" + " "*23 + "║")
    logger.info("╚" + "="*58 + "╝")
    
    tests = [
        ("模拟数据提供者", test_mock_data_provider),
        ("策略分析器", test_strategy_analyzer),
        ("邮件通知器", test_email_notifier),
        ("集成测试", test_market_pulse_integration),
        ("Akshare+故障转移", test_akshare_with_fallback),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ 测试异常: {e}", exc_info=True)
            results.append((test_name, False))
    
    # 汇总
    logger.info("\n\n" + "="*60)
    logger.info("测试汇总")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n总计: {passed}/{total} 通过")
    logger.info("="*60 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
