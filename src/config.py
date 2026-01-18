#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""配置管理模块"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器 - 处理 config.json 和环境变量"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._load_env_vars()

    def _load_config(self) -> None:
        """从 JSON 文件加载配置"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    def _load_env_vars(self) -> None:
        """加载并替换配置中的环境变量"""
        self._replace_env_vars(self.config)

    def _replace_env_vars(self, obj: Any) -> None:
        """递归替换对象中的 ${VAR} 为环境变量值"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    obj[key] = os.getenv(env_var, value)
                else:
                    self._replace_env_vars(value)
        elif isinstance(obj, list):
            for item in obj:
                self._replace_env_vars(item)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点表示法（如 'email.sender'）"""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_stocks(self) -> list:
        """获取监控的股票列表"""
        return self.get("stocks.watchlist", [])

    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        return self.get("notification.email", {})

    def get_strategies(self) -> list:
        """获取所有启用的策略"""
        strategies = self.get("strategies", [])
        return [s for s in strategies if s.get("enabled", True)]

    def get_strategy(self, name: str) -> Optional[Dict[str, Any]]:
        """获取特定策略配置"""
        strategies = self.get("strategies", [])
        for strategy in strategies:
            if strategy.get("name") == name:
                return strategy
        return None

    def get_data_source(self) -> Dict[str, Any]:
        """获取数据源配置"""
        return self.get("data_source", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})
