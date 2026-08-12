# -*- coding: utf-8 -*-
"""用昨天的数据测试信号"""

import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from src.strategies.scanner import MarketScanner
from src.core.signal_generator import SignalGenerator

scanner = MarketScanner()
sg = SignalGenerator()

print("=" * 60)
print("用昨天的数据测试信号")
print("=" * 60)

# 获取数据
symbols = scanner.get_us_stock_symbols()
print(f"\n扫描 {len(symbols)} 个美股...")

results = {'buy': [], 'short': []}

for symbol in symbols:
    data = scanner.data_manager.fetch_klines(symbol, '4H', 200)
    if data is None:
        continue
    
    # 使用倒数第二根K线（昨天的数据）
    if len(data['prices']) < 2:
        continue
    
    # 构建昨天的indicators
    prices_yesterday = data['prices'][:-1]
    volumes_yesterday = data['volumes'][:-1]
    
    if len(prices_yesterday) < 50:
        continue
    
    indicators = sg.calculate_indicators(prices_yesterday, volumes_yesterday)
    if indicators is None:
        continue
    
    # 用昨天的大盘趋势（假设也是bullish）
    market_trend = 'bullish'
    
    signal, score, reasons, strategy_type = sg.generate_signal(indicators, market_trend)
    
    if signal == 'buy':
        results['buy'].append({
            'symbol': symbol,
            'rsi': indicators['rsi'],
            'price': indicators['current'],
            'score': score,
            'reasons': reasons
        })
    elif signal == 'short':
        results['short'].append({
            'symbol': symbol,
            'rsi': indicators['rsi'],
            'price': indicators['current'],
            'score': score,
            'reasons': reasons
        })

# 显示结果
print(f"\n" + "=" * 60)
print(f"昨天的数据测试结果")
print("=" * 60)

print(f"\n【做多信号】{len(results['buy'])} 个")
for r in results['buy'][:10]:
    print(f"  {r['symbol']:<20} RSI:{r['rsi']:.1f} 价格:{r['price']:.2f} 得分:{r['score']}")

print(f"\n【做空信号】{len(results['short'])} 个")
for r in results['short'][:10]:
    print(f"  {r['symbol']:<20} RSI:{r['rsi']:.1f} 价格:{r['price']:.2f} 得分:{r['score']}")

print(f"\n" + "=" * 60)
print(f"结论: 昨天有 {len(results['buy'])} 个买入信号，{len(results['short'])} 个做空信号")
print("=" * 60)
