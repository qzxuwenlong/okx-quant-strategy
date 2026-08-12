# -*- coding: utf-8 -*-
"""
当前策略版本确认
版本：v2.0（区分趋势跟随/均值回归）
回测结果：收益1.40%, 胜率59.57%, 盈亏比1.71
"""

# 策略特点
STRATEGY_FEATURES = {
    "版本": "v2.0",
    "策略逻辑": "大周期定方向，小周期找时机",
    "做多条件": [
        "大盘bullish: 趋势跟随，价格>MA50, RSI<65",
        "大盘bearish: RSI<25超卖反弹（小仓位）",
        "大盘neutral: RSI<30均值回归"
    ],
    "做空条件": [
        "大盘bearish: 趋势跟随，价格<MA50, RSI>35",
        "大盘neutral: RSI>70+欧奈尔信号"
    ],
    "回测结果": {
        "总收益": "1.40%",
        "胜率": "59.57%",
        "盈亏比": "1.71",
        "最大回撤": "1.54%",
        "交易数": "47笔"
    }
}

# 使用方法
print("=" * 60)
print("当前策略版本：v2.0")
print("=" * 60)
print()
print("策略特点：")
print("  1. 区分趋势跟随和均值回归")
print("  2. 大周期定方向，小周期找时机")
print("  3. 大盘bearish时避免追多，RSI<35时避免追空")
print()
print("回测结果（SPY，50天）：")
print("  收益：1.40%")
print("  胜率：59.57%")
print("  盈亏比：1.71")
print("  最大回撤：1.54%")
print()
print("使用方法：")
print("  py src/strategies/scanner.py  # 扫描信号")
print("  py run_backtest_new.py        # 回测验证")
print()
print("文件位置：")
print("  策略代码：src/core/signal_generator.py")
print("  扫描器：src/strategies/scanner.py")
print("  回测器：run_backtest_new.py")
print()
