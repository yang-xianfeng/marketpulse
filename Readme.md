# 📊 MarketPulse - Daily Beat

**自动化股票监控系统**

自动分析收盘后的市场走势，根据技术策略发送通知到您的邮箱。永远不要错过市场节拍。

---

## ✨ 核心功能

- 📈 **自动监控**: 定时监控自选股票的价格走势
- 📊 **技术分析**: 计算 5/10/20 日移动平均线
- 🔔 **智能通知**: 触发交易信号时通过邮件通知
- 🚀 **自动部署**: GitHub Actions 自动化运行
- 🛡️ **容错设计**: Akshare 失效时自动转移到模拟数据
- 📝 **详细日志**: 完整的操作记录和错误追踪

---

## 🚀 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python test_strategy.py
python stock_strategy.py
```

### GitHub Actions 部署

```bash
git push origin main
# 配置 EMAIL_CONFIG Secret
# 完成！程序将在每个交易日下午 3 点自动运行
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICK_START.md](QUICK_START.md) | ⚡ 快速入门 |
| [USAGE.md](USAGE.md) | 📖 详细使用指南 |
| [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md) | 📝 重构总结 |
| [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) | ✅ 完成报告 |

---

## ✅ 测试状态

```
✓ 单元测试: 5/5 通过
✓ 集成测试: 成功
✓ 故障转移: 工作正常
✓ 邮件通知: 已验证
```

---

## 📊 策略说明

### 技术指标
- **5 日均线 (MA5)**: 短期趋势
- **10 日均线 (MA10)**: 中期趋势  
- **20 日均线 (MA20)**: 长期趋势

### 交易信号
- 🔴 **减仓**: 股价跌破 5 日均线
- 🟠 **再减仓**: 股价跌破 10 日均线
- 🔴 **清仓**: 股价跌破 20 日均线

---

## 📋 版本信息

**v2.0 (2026-01-18) - 生产级重构** ✨
- ✨ 故障转移机制
- ✨ 完整错误处理
- ✨ 模块化架构
- ✨ 完整单元测试 (5/5)
- 🐛 修复 KeyError: 'date'
- 🔒 配置外部化

**版本**: 2.0  
**状态**: ✅ 生产就绪  
**许可证**: MIT License
