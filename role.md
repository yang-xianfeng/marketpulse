这个项目的目标是利用 GitHub Actions 定时运行 Python 脚本，获取自选股票集的实时行情，按照特定策略（例如，股票破5日线、10日线、20日线进行减仓、清仓操作）进行操作，并在策略触发时通过 QQ 邮箱进行通知。下面我将从专业角度分析并给出详细的指引文档，涉及的技术栈包括 GitHub Actions、Python、Akshare、邮箱通知等。

### 项目需求分析

1. **GitHub Actions 定时任务**：

   * **功能**：每天定时运行 Python 脚本。
   * **调度频率**：每天一次，调用上限为每月 1000 次，可以通过 GitHub Actions 配置 cron 来实现。
2. **Python 股票策略分析**：

   * **自选股票集**：允许用户定义自选股票（可以通过输入股票代码的列表或者通过文件上传）。
   * **行情获取**：通过 `akshare` 库获取当日股市行情。
   * **策略实现**：根据股价相对于 5日、10日、20日均线的表现进行买卖策略（减仓、清仓等）。
3. **邮件通知**：

   * **通知方式**：使用 QQ 邮箱（SMTP）发送通知邮件，告知用户股市策略触发的情况。

### 项目模块设计

1. **GitHub Actions 配置**

   * 配置定时任务，每天定时执行 Python 脚本。
   * 使用 cron 表达式配置 GitHub Actions 的触发周期。

2. **Python 脚本设计**

   * 获取自选股票集的实时行情。
   * 对每只股票进行 5日、10日、20日均线的计算。
   * 根据策略触发买卖操作。
   * 向指定的 QQ 邮箱发送通知。

3. **QQ 邮箱发送通知**

   * 配置 QQ 邮箱的 SMTP 服务，获取授权码，用于发送邮件。

### 具体实现步骤

#### 1. GitHub Actions 配置

在 GitHub 仓库中，创建 `.github/workflows/stock_strategy.yml` 文件：

```yaml
name: Stock Strategy Task

on:
  schedule:
    - cron: '0 18 * * *'  # 每天 18:00（可根据需要调整时间）

jobs:
  run_stock_strategy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout the repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run the stock strategy script
      run: |
        python stock_strategy.py
```

* **解释**：

  * `schedule` 配置表示每天 18:00 自动执行。
  * `run_stock_strategy` 任务依次执行：检查出代码、设置 Python 环境、安装依赖、运行 `stock_strategy.py` 脚本。

#### 2. Python 脚本设计

**主要功能**：

1. 获取自选股票集的行情数据。
2. 计算 5日、10日、20日的移动平均线。
3. 判断是否触发减仓、清仓策略。
4. 如果触发策略，通过 QQ 邮箱通知。

##### `stock_strategy.py` 示例代码

```python
import akshare as ak
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import numpy as np

# 用户自选股票列表（示例）
stock_list = ['002738', '159545', '159915']  # 这里需要用户传入自选股票代码

# 获取股票数据的函数
def get_stock_data(stock_code):
    stock_data = ak.stock_zh_a_daily(symbol=stock_code)
    return stock_data

# 计算移动平均线
def calculate_moving_average(stock_data, days):
    stock_data['MA' + str(days)] = stock_data['close'].rolling(window=days).mean()
    return stock_data

# 检查是否触发减仓或清仓策略
def check_strategy(stock_data):
    latest_data = stock_data.iloc[-1]
    if latest_data['close'] < latest_data['MA5']:
        return "减仓：股票已破5日线"
    elif latest_data['close'] < latest_data['MA10']:
        return "再减仓：股票已破10日线"
    elif latest_data['close'] < latest_data['MA20']:
        return "清仓：股票已破20日线"
    else:
        return None

# 发送邮件通知
def send_email(subject, body):
    sender_email = "your_email@qq.com"
    receiver_email = "receiver_email@qq.com"
    password = "your_smtp_password"  # QQ邮箱授权码

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"邮件发送失败: {e}")

# 主流程
def main():
    for stock_code in stock_list:
        stock_data = get_stock_data(stock_code)
        stock_data = calculate_moving_average(stock_data, 5)
        stock_data = calculate_moving_average(stock_data, 10)
        stock_data = calculate_moving_average(stock_data, 20)

        result = check_strategy(stock_data)
        if result:
            subject = f"股票策略触发：{stock_code}"
            body = f"股票 {stock_code} 触发了以下策略：\n\n{result}"
            send_email(subject, body)

if __name__ == "__main__":
    main()
```

#### 3. 配置邮件通知（QQ邮箱）

1. 你需要在 QQ 邮箱中开启 SMTP 服务，并获取授权码。操作步骤如下：

   * 登录 QQ 邮箱，进入设置 → "账户" → "POP3/SMTP/IMAP" 设置，开启 SMTP 服务，并生成授权码。
2. 在 `send_email` 函数中，填入你的邮箱地址和授权码。

#### 4. 安装依赖

在项目根目录下创建 `requirements.txt` 文件，列出所需的 Python 包：

```txt
akshare
pandas
numpy
smtplib
```

### 项目调试与部署

1. **本地调试**：

   * 在本地运行 `stock_strategy.py` 脚本进行调试，确保能够获取股票数据、计算均线并发送邮件通知。

2. **部署到 GitHub**：

   * 将代码推送到 GitHub 仓库。
   * GitHub Actions 会根据配置的定时任务自动运行脚本。

3. **邮件内容定制**：

   * 你可以根据需要定制邮件内容，例如包括更多的股票分析信息，或者包含触发策略的更多细节。

### 性能与优化建议

1. **数据处理优化**：股票数据获取、计算均线等操作可能较为耗时，建议加入缓存机制，避免重复获取和计算相同的数据。
2. **错误处理**：对 `akshare` 获取数据、邮件发送等关键操作增加异常处理，避免任务执行中断。
3. **股票策略优化**：可以根据实际需求，加入更多的策略和参数调整，例如加入其他技术指标（如MACD、RSI等）。

### 总结

本项目通过 GitHub Actions 定时执行 Python 脚本，利用 Akshare 获取股票数据，基于简单的移动均线策略进行股票分析，并通过 QQ 邮箱发送通知。开发过程中需要关注数据获取的频率、策略的灵活性以及邮件通知的可靠性。