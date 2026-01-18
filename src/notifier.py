#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""邮件和通知模块"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmailNotifier:
    """邮件通知器 - 从环境变量和配置读取邮箱信息"""

    def __init__(self, email_config: Dict[str, str]):
        """
        初始化邮件通知器

        Args:
            email_config: 邮件配置字典，包含：
                - sender: 发件人邮箱
                - receiver: 收件人邮箱
                - smtp_server: SMTP 服务器地址
                - smtp_port: SMTP 端口
                - auth_code_env: 邮箱授权码环境变量名
        """
        self.config = email_config
        self.sender = email_config.get("sender", "")
        self.receiver = email_config.get("receiver", "")
        self.smtp_server = email_config.get("smtp_server", "smtp.qq.com")
        self.smtp_port = int(email_config.get("smtp_port", 465))

        # 从环境变量获取授权码
        import os

        auth_code_env = email_config.get("auth_code_env", "SMTP_AUTH_CODE")
        self.auth_code = os.getenv(auth_code_env, "")

        self._validate_config()

    def _validate_config(self) -> None:
        """验证配置是否完整"""
        if not self.sender:
            logger.warning("未配置发件人邮箱 (SENDER_EMAIL)")
        if not self.receiver:
            logger.warning("未配置收件人邮箱 (RECEIVER_EMAIL)")
        if not self.auth_code:
            logger.warning("未配置邮箱授权码 (SMTP_AUTH_CODE)")

    def send(
        self, subject: str, body: str, html: bool = False
    ) -> bool:
        """
        发送邮件

        Args:
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式

        Returns:
            是否发送成功
        """
        if not self._is_configured():
            logger.warning("邮件配置不完整，邮件未发送")
            logger.info(f"邮件主题: {subject}\n邮件正文:\n{body}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender
            msg["To"] = self.receiver
            msg["Subject"] = subject

            # 添加邮件内容
            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type, "utf-8"))

            logger.info(f"发送邮件: {subject}")

            # 连接 SMTP 服务器并发送
            with smtplib.SMTP_SSL(
                self.smtp_server, self.smtp_port, timeout=10
            ) as server:
                server.login(self.sender, self.auth_code)
                server.sendmail(self.sender, self.receiver, msg.as_string())

            logger.info("邮件发送成功")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP 认证失败，请检查邮箱地址和授权码")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}", exc_info=True)
            return False

    def _is_configured(self) -> bool:
        """检查配置是否完整"""
        return bool(self.sender and self.receiver and self.auth_code)


class Notifier:
    """通知器 - 支持多种通知方式"""

    def __init__(self, notification_config: Dict = None):
        """
        初始化通知器

        Args:
            notification_config: 通知配置字典
        """
        self.config = notification_config or {}
        self.enabled = self.config.get("enabled", True)

        self.email_notifier = None
        if self.config.get("email", {}).get("enabled", True):
            self.email_notifier = EmailNotifier(self.config.get("email", {}))

    def notify(self, subject: str, body: str) -> bool:
        """发送通知"""
        if not self.enabled:
            logger.warning("通知已禁用")
            return False

        success = True

        # 尝试发送邮件
        if self.email_notifier:
            if not self.email_notifier.send(subject, body):
                success = False

        return success
