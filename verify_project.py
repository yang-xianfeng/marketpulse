#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarketPulse v1.0.0 - 项目完成验证脚本
验证所有关键文件和功能的完整性
"""

import os
import json
from pathlib import Path


def check_project_structure():
    """检查项目结构完整性"""
    print("\n" + "=" * 60)
    print("MarketPulse v1.0.0 - 项目完整性检查")
    print("=" * 60)

    required_files = {
        "源代码": [
            "main.py",
            "src/__init__.py",
            "src/app.py",
            "src/config.py",
            "src/logger.py",
            "src/providers.py",
            "src/strategies.py",
            "src/analyzer.py",
            "src/notifier.py",
        ],
        "配置文件": [
            "config.json",
            ".env.example",
            "requirements.txt",
        ],
        "文档": [
            "README.md",
            "QUICKSTART.md",
            "DEVELOPMENT.md",
            "SECURITY.md",
            "CHANGELOG.md",
        ],
        "GitHub Actions": [
            ".github/workflows/daily-analysis.yml",
            ".github/workflows/test.yml",
        ],
        "版本控制": [
            ".gitignore",
        ],
    }

    all_exist = True

    for category, files in required_files.items():
        print(f"\n✓ {category}")
        for file_path in files:
            full_path = Path(file_path)
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"  ✓ {file_path:40} ({size:,} bytes)")
            else:
                print(f"  ✗ {file_path:40} (不存在)")
                all_exist = False

    return all_exist


def check_config_validity():
    """检查配置文件有效性"""
    print("\n" + "=" * 60)
    print("配置文件验证")
    print("=" * 60)

    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        print("\n✓ config.json 格式正确")
        print(f"  • 监控股票: {config.get('stocks', {}).get('watchlist', [])}")
        print(f"  • 邮件通知: {config.get('notification', {}).get('enabled', False)}")
        print(f"  • 策略数量: {len(config.get('strategies', []))}")
        print(f"  • 数据源: {config.get('data_source', {}).get('primary', 'unknown')}")

        required_keys = ["stocks", "notification", "strategies", "data_source"]
        for key in required_keys:
            if key not in config:
                print(f"  ✗ 缺少关键配置: {key}")
                return False

        return True

    except Exception as e:
        print(f"✗ config.json 格式错误: {e}")
        return False


def check_syntax():
    """检查 Python 文件语法"""
    print("\n" + "=" * 60)
    print("Python 语法检查")
    print("=" * 60)

    import py_compile

    python_files = [
        "main.py",
        "src/app.py",
        "src/config.py",
        "src/logger.py",
        "src/providers.py",
        "src/strategies.py",
        "src/analyzer.py",
        "src/notifier.py",
    ]

    all_valid = True
    for file in python_files:
        try:
            py_compile.compile(file, doraise=True)
            print(f"✓ {file:40} 语法正确")
        except py_compile.PyCompileError as e:
            print(f"✗ {file:40} 语法错误: {e}")
            all_valid = False

    return all_valid


def check_imports():
    """检查关键导入"""
    print("\n" + "=" * 60)
    print("导入验证")
    print("=" * 60)

    try:
        print("✓ 导入核心模块...")
        from src.config import ConfigManager
        from src.logger import setup_logger
        from src.providers import AkshareProvider, MockProvider, FallbackProvider
        from src.strategies import StrategyFactory, Strategy
        from src.analyzer import StockAnalyzer
        from src.notifier import Notifier
        from src.app import MarketPulse

        print("  ✓ ConfigManager")
        print("  ✓ setup_logger")
        print("  ✓ AkshareProvider")
        print("  ✓ MockProvider")
        print("  ✓ FallbackProvider")
        print("  ✓ StrategyFactory")
        print("  ✓ StockAnalyzer")
        print("  ✓ Notifier")
        print("  ✓ MarketPulse")

        return True

    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("依赖包检查")
    print("=" * 60)

    required_packages = {
        "pandas": "数据处理",
        "numpy": "数值计算",
        "requests": "网络请求",
    }

    all_installed = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package:20} ({description})")
        except ImportError:
            print(f"✗ {package:20} 未安装")
            all_installed = False

    return all_installed


def check_functionality():
    """检查基本功能"""
    print("\n" + "=" * 60)
    print("功能验证")
    print("=" * 60)

    try:
        from src.config import ConfigManager

        print("✓ 配置管理")
        config = ConfigManager("config.json")
        stocks = config.get_stocks()
        print(f"  • 成功读取 {len(stocks)} 只股票")

        print("✓ 数据提供者")
        from src.providers import MockProvider

        provider = MockProvider()
        data = provider.fetch("002738")
        print(f"  • 成功生成模拟数据 ({len(data)} 行)")

        print("✓ 策略系统")
        from src.strategies import StrategyFactory

        strategy = StrategyFactory.create("moving_average", {
            "params": {
                "periods": [5, 10, 20],
                "signals": {}
            }
        })
        print(f"  • 成功创建策略: {strategy.name}")

        print("✓ 分析器")
        from src.analyzer import StockAnalyzer

        analyzer = StockAnalyzer(provider, config.get_strategies())
        result = analyzer.analyze("002738")
        print(f"  • 成功分析股票: {result is not None}")

        return True

    except Exception as e:
        print(f"✗ 功能验证失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def print_summary(checks):
    """打印检查总结"""
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)

    passed = sum(1 for check in checks.values() if check)
    total = len(checks)

    print(f"\n通过: {passed}/{total}")

    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {check_name}")

    if passed == total:
        print("\n" + "=" * 60)
        print("🎉 所有检查通过！项目已就绪。")
        print("=" * 60)
        print("\n快速开始:")
        print("  1. cp .env.example .env")
        print("  2. 编辑 .env 填入邮箱信息")
        print("  3. python main.py")
        print()
    else:
        print("\n" + "=" * 60)
        print("⚠️  有些检查失败。请检查上述错误。")
        print("=" * 60)
        print()

    return passed == total


def main():
    """主检查函数"""
    checks = {
        "项目结构": check_project_structure(),
        "配置有效性": check_config_validity(),
        "Python 语法": check_syntax(),
        "导入验证": check_imports(),
        "依赖包": check_dependencies(),
        "基本功能": check_functionality(),
    }

    success = print_summary(checks)
    return 0 if success else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
