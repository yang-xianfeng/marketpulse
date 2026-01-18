#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarketPulse - 股票策略监控系统
功能：监控自选股票，当触发策略时发送邮件通知

使用方法:
    python main.py
"""

from src.app import main

if __name__ == "__main__":
    main(config_file="config.json")
