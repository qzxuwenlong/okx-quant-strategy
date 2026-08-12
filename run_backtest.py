# -*- coding: utf-8 -*-
"""快速回测测试"""

import sys
sys.path.insert(0, '.')

from src.strategies.backtester import Backtester

# 创建回测器
bt = Backtester(initial_capital=10000)

# 回测SPY（大盘）
print("=" * 60)
print("回测 SPY-USDT-SWAP（大盘）")
print("=" * 60)
results = bt.run_backtest('SPY-USDT-SWAP')

if results:
    from src.strategies.backtester import format_report
    print(format_report(results))
