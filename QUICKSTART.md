# MarketPulse 快速开始

## 5 分钟快速上手

### 1. 克隆并安装

```bash
git clone https://github.com/yang-xianfeng/marketpulse.git
cd marketpulse
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env（使用你的编辑器）
# SENDER_EMAIL=your_email@qq.com
# RECEIVER_EMAIL=receiver@qq.com
# SMTP_AUTH_CODE=your_16_digit_code
```

### 3. 编辑股票列表

编辑 `config.json` 的 `stocks.watchlist`：

```json
{
  "stocks": {
    "watchlist": ["002738", "159545", "159915"]
  }
}
```

### 4. 运行分析

```bash
python main.py
```

## 常见问题

### Q: 如何获取 QQ 邮箱授权码？

A: 
1. 登录 [QQ 邮箱](https://mail.qq.com)
2. 进入 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务**
4. 点击 **开启服务**
5. 按照提示获取 **16 位授权码**

### Q: 程序找不到 config.json？

A: 确保在项目根目录运行：

```bash
cd /path/to/marketpulse
python main.py
```

### Q: 邮件没有发送？

A: 检查以下几点：

1. 环境变量是否正确设置：
   ```bash
   echo $SENDER_EMAIL
   echo $SMTP_AUTH_CODE
   ```

2. 授权码是否正确（16 位）

3. 检查日志中的错误信息：
   ```bash
   tail marketpulse.log
   ```

### Q: 数据获取失败怎么办？

A: 程序会自动使用模拟数据，继续运行。如果要使用真实数据：

1. 检查网络连接
2. 更新 akshare：`pip install --upgrade akshare`
3. 查看具体错误：运行时会在日志中显示

## 核心概念速览

### 3 个主要对象

1. **StockAnalyzer** - 分析股票
   ```python
   analyzer = StockAnalyzer(provider, strategies)
   result = analyzer.analyze("002738")
   ```

2. **Strategy** - 分析策略
   ```python
   # 移动平均线策略已内置
   # 可添加自己的策略，见 DEVELOPMENT.md
   ```

3. **Notifier** - 发送通知
   ```python
   notifier = Notifier(notification_config)
   notifier.notify("标题", "内容")
   ```

## 配置选项详解

### 启用/禁用邮件通知

```json
{
  "notification": {
    "enabled": true,           // 总开关
    "email": {
      "enabled": true          // 邮件通知开关
    }
  }
}
```

### 修改分析策略

```json
{
  "strategies": [
    {
      "enabled": true,
      "params": {
        "periods": [5, 10, 20]  // 修改均线周期
      }
    }
  ]
}
```

### 修改日志级别

```json
{
  "logging": {
    "level": "DEBUG"            // 可选：DEBUG, INFO, WARNING, ERROR
  }
}
```

## 下一步

- 📖 详细文档：[README.md](README.md)
- 🛠️ 开发指南：[DEVELOPMENT.md](DEVELOPMENT.md)
- 🔒 安全说明：[SECURITY.md](SECURITY.md)
- 💻 代码示例：[examples.py](examples.py)

## 获得帮助

- 查看日志文件：`marketpulse.log`
- 查看源代码：`src/` 目录
- 提交 Issue：GitHub Issues
