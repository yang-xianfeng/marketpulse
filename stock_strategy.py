#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarketPulse - 股票策略监控系统
功能：监控自选股票，当触发移动平均线策略时发送邮件通知
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from pathlib import Path
import json


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockDataProvider:
    """股票数据提供者基类"""
    
    def get_stock_data(self, stock_code: str) -> pd.DataFrame:
        """获取股票数据，返回包含 'date' 和 'close' 列的 DataFrame"""
        raise NotImplementedError


class AkshareProvider(StockDataProvider):
    """使用 akshare 获取数据的提供者（带有故障转移机制）"""
    
    def __init__(self, fallback_provider: Optional[StockDataProvider] = None):
        self.fallback_provider = fallback_provider
    
    def get_stock_data(self, stock_code: str) -> pd.DataFrame:
        """获取股票数据，支持故障转移"""
        try:
            import akshare as ak
            
            # 添加 sh/sz 前缀
            symbol = self._format_symbol(stock_code)
            
            logger.info(f"从 akshare 获取 {stock_code} 的数据")
            data = ak.stock_zh_a_daily(symbol=symbol)
            
            # 验证数据格式
            if 'date' not in data.columns and len(data.columns) > 0:
                logger.warning(f"akshare 返回的列名: {data.columns.tolist()}")
                # 尝试自动修复列名
                data = self._fix_column_names(data)
            
            return data
            
        except Exception as e:
            logger.error(f"akshare 获取数据失败: {e}")
            
            # 使用故障转移提供者
            if self.fallback_provider:
                logger.info(f"尝试使用故障转移提供者获取 {stock_code} 的数据")
                return self.fallback_provider.get_stock_data(stock_code)
            
            raise
    
    @staticmethod
    def _format_symbol(stock_code: str) -> str:
        """格式化股票代码"""
        if stock_code.startswith('1'):  # 基金代码
            return f'sz{stock_code}' if not stock_code.startswith('sz') else stock_code
        elif stock_code.startswith('6'):  # 上证
            return f'sh{stock_code}' if not stock_code.startswith('sh') else stock_code
        else:  # 默认深证
            return f'sz{stock_code}' if not stock_code.startswith('sz') else stock_code
    
    @staticmethod
    def _fix_column_names(data: pd.DataFrame) -> pd.DataFrame:
        """修复列名（akshare API 变化的兼容处理）"""
        # 映射可能的列名
        column_mapping = {
            'trade_date': 'date',
            '日期': 'date',
            '时间': 'date',
            'open_price': 'open',
            '开盘': 'open',
            'close_price': 'close',
            '收盘': 'close',
            'high_price': 'high',
            '最高': 'high',
            'low_price': 'low',
            '最低': 'low',
            'volume': 'volume',
            '成交量': 'volume',
        }
        
        # 重命名列
        for old_col, new_col in column_mapping.items():
            if old_col in data.columns:
                data = data.rename(columns={old_col: new_col})
        
        return data


class MockDataProvider(StockDataProvider):
    """模拟数据提供者（用于测试和故障转移）"""
    
    def get_stock_data(self, stock_code: str) -> pd.DataFrame:
        """生成模拟数据"""
        logger.info(f"使用模拟数据生成 {stock_code} 的数据")
        
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        np.random.seed(hash(stock_code) % 2**32)
        
        base_price = 10 + (hash(stock_code) % 100) / 10
        prices = base_price + np.cumsum(np.random.randn(60) * 0.5)
        
        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(60) * 0.3,
            'close': prices,
            'high': prices + np.abs(np.random.randn(60) * 0.3),
            'low': prices - np.abs(np.random.randn(60) * 0.3),
            'volume': np.random.randint(1000000, 10000000, 60),
        })


class StockStrategyAnalyzer:
    """股票策略分析器"""
    
    def __init__(self, data_provider: StockDataProvider):
        self.data_provider = data_provider
        self.ma_days = [5, 10, 20]  # 移动平均线的天数
    
    def analyze(self, stock_code: str) -> Optional[Dict[str, str]]:
        """分析股票，返回策略触发信息"""
        try:
            logger.info(f"分析股票 {stock_code}")
            
            # 获取数据
            stock_data = self.data_provider.get_stock_data(stock_code)
            
            if stock_data is None or len(stock_data) == 0:
                logger.warning(f"无法获取 {stock_code} 的数据")
                return None
            
            # 确保有必要的列
            if 'close' not in stock_data.columns:
                logger.error(f"{stock_code} 数据缺少 'close' 列")
                return None
            
            # 计算移动平均线
            for days in self.ma_days:
                stock_data[f'MA{days}'] = stock_data['close'].rolling(window=days).mean()
            
            # 检查策略
            latest = stock_data.iloc[-1]
            latest_date = stock_data['date'].iloc[-1] if 'date' in stock_data.columns else '未知日期'
            latest_price = latest['close']
            
            # 检查是否触发策略
            signals = []
            
            if pd.notna(latest['MA5']) and latest_price < latest['MA5']:
                signals.append(f"价格 ({latest_price:.2f}) 已跌破5日均线 ({latest['MA5']:.2f}) - 建议减仓")
            
            if pd.notna(latest['MA10']) and latest_price < latest['MA10']:
                signals.append(f"价格 ({latest_price:.2f}) 已跌破10日均线 ({latest['MA10']:.2f}) - 建议再减仓")
            
            if pd.notna(latest['MA20']) and latest_price < latest['MA20']:
                signals.append(f"价格 ({latest_price:.2f}) 已跌破20日均线 ({latest['MA20']:.2f}) - 建议清仓")
            
            if signals:
                return {
                    'code': stock_code,
                    'date': str(latest_date),
                    'price': latest_price,
                    'signals': '\n'.join(signals)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"分析股票 {stock_code} 时出错: {e}", exc_info=True)
            return None


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, config_file: str = 'email_config.json'):
        """初始化邮件配置"""
        self.config = self._load_config(config_file)
    
    @staticmethod
    def _load_config(config_file: str) -> Dict:
        """从配置文件加载邮件设置"""
        config_path = Path(config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        # 返回默认配置（需要用户修改）
        return {
            'sender_email': 'your_email@qq.com',
            'receiver_email': 'receiver_email@qq.com',
            'password': 'your_smtp_password',  # QQ 邮箱授权码
            'smtp_server': 'smtp.qq.com',
            'smtp_port': 465,
            'enabled': False  # 默认禁用邮件发送
        }
    
    def send(self, subject: str, body: str) -> bool:
        """发送邮件"""
        if not self.config.get('enabled', False):
            logger.warning("邮件发送已禁用，请在配置中启用")
            logger.info(f"邮件主题: {subject}\n邮件内容:\n{body}")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['receiver_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            logger.info(f"发送邮件: {subject}")
            
            with smtplib.SMTP_SSL(
                self.config['smtp_server'],
                self.config['smtp_port'],
                timeout=10
            ) as server:
                server.login(self.config['sender_email'], self.config['password'])
                server.sendmail(
                    self.config['sender_email'],
                    self.config['receiver_email'],
                    msg.as_string()
                )
            
            logger.info("邮件发送成功")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("邮箱认证失败，请检查用户名和密码（授权码）")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}", exc_info=True)
            return False


class MarketPulse:
    """MarketPulse 主类"""
    
    def __init__(
        self,
        stock_list: List[str],
        data_provider: Optional[StockDataProvider] = None,
        notifier: Optional[EmailNotifier] = None
    ):
        self.stock_list = stock_list
        self.data_provider = data_provider or AkshareProvider(MockDataProvider())
        self.analyzer = StockStrategyAnalyzer(self.data_provider)
        self.notifier = notifier or EmailNotifier()
    
    def run(self) -> None:
        """运行策略分析"""
        logger.info(f"开始分析 {len(self.stock_list)} 只股票: {self.stock_list}")
        
        triggered_stocks = []
        
        for stock_code in self.stock_list:
            result = self.analyzer.analyze(stock_code)
            
            if result:
                triggered_stocks.append(result)
                logger.info(f"股票 {stock_code} 触发策略")
                
                # 发送通知
                subject = f"【MarketPulse】股票策略触发: {stock_code}"
                body = f"""
股票代码: {result['code']}
交易日期: {result['date']}
当前价格: {result['price']:.2f}

触发信号:
{result['signals']}

---
MarketPulse - Daily Beat
https://github.com/yang-xianfeng/marketpulse
"""
                self.notifier.send(subject, body)
            else:
                logger.info(f"股票 {stock_code} 无触发信号")
        
        # 生成汇总日志
        self._log_summary(triggered_stocks)
    
    @staticmethod
    def _log_summary(triggered_stocks: List[Dict]) -> None:
        """记录汇总信息"""
        logger.info(f"\n{'='*50}")
        logger.info(f"分析完成，共触发 {len(triggered_stocks)} 只股票")
        
        for stock in triggered_stocks:
            logger.info(f"- {stock['code']}: {stock['date']}, 价格 {stock['price']:.2f}")
        
        logger.info(f"{'='*50}\n")


# 主程序
def main():
    # 自选股票列表
    stock_list = ['002738', '159545', '159915']
    
    try:
        # 初始化 MarketPulse
        market_pulse = MarketPulse(
            stock_list=stock_list,
            data_provider=AkshareProvider(MockDataProvider()),
            notifier=EmailNotifier('email_config.json')
        )
        
        # 运行分析
        market_pulse.run()
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
