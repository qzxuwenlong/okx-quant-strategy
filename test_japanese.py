# -*- coding: utf-8 -*-
"""测试日本策略"""

import sys
sys.path.insert(0, '.')

from src.core.japanese_strategy import JapanesePatterns, CIStrategy, BNFStrategy
from src.core.comprehensive_signal import ComprehensiveSignalGenerator
import numpy as np

print("=" * 60)
print("日本交易策略测试")
print("=" * 60)

# 1. 测试蜡烛图形态
print("\n[1] 蜡烛图形态识别")
patterns = JapanesePatterns()

# 模拟锤子线
hammer = {'open': 100, 'high': 101, 'low': 95, 'close': 100.5}
is_hammer = patterns.is_hammer(hammer['open'], hammer['high'], hammer['low'], hammer['close'])
print(f"锤子线: {is_hammer}")

# 模拟看涨吞没
is_engulfing = patterns.is_engulfing_bullish(105, 100, 99, 106)
print(f"看涨吞没: {is_engulfing}")

# 2. 测试cis策略
print("\n[2] cis日内动量策略")
cis = CIStrategy()

# 模拟数据
import pandas as pd
df = pd.DataFrame({
    'close': [100, 101, 102, 103, 104, 105, 104, 103, 106, 107],
    'high': [101, 102, 103, 104, 105, 106, 105, 104, 107, 108],
    'low': [99, 100, 101, 102, 103, 104, 103, 102, 105, 106],
    'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1400, 1300, 2000, 2100]
})

signal, score, reasons = cis.generate_signal(df)
print(f"信号: {signal}, 得分: {score}, 原因: {reasons}")

# 3. 测试BNF策略
print("\n[3] BNF大波段策略")
bnf = BNFStrategy()

# 模拟长期数据
prices = [100 + i * 0.5 + np.random.randn() * 2 for i in range(250)]
df_long = pd.DataFrame({
    'close': prices,
    'high': [p + abs(np.random.randn()) for p in prices],
    'low': [p - abs(np.random.randn()) for p in prices],
    'volume': [1000 + np.random.randint(-100, 100) for _ in range(250)]
})

signal, score, reasons = bnf.generate_signal(df_long)
print(f"信号: {signal}, 得分: {score}, 原因: {reasons}")

# 4. 测试综合信号生成器
print("\n[4] 综合信号生成器")
generator = ComprehensiveSignalGenerator()

# 模拟完整数据
prices = [100 + i * 0.3 + np.random.randn() for i in range(100)]
volumes = [1000 + np.random.randint(-200, 200) for _ in range(100)]
opens = [p - np.random.rand() for p in prices]
highs = [p + abs(np.random.randn()) for p in prices]
lows = [p - abs(np.random.randn()) for p in prices]

indicators = generator.calculate_indicators(prices, volumes, opens, highs, lows)
if indicators:
    signal, score, reasons, confirm_type, strategy = generator.generate_comprehensive_signal(indicators, 'bullish')
    print(f"信号: {signal}")
    print(f"得分: {score}")
    print(f"原因: {reasons}")
    print(f"确认类型: {confirm_type}")
    print(f"策略来源: {strategy}")

print("\n" + "=" * 60)
print("日本策略测试完成")
print("=" * 60)
