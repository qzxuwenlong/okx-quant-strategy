# -*- coding: utf-8 -*-
"""调试：检查信号生成过程"""

import sys
sys.path.insert(0, '.')

from src.strategies.scanner import MarketScanner
from src.core.signal_generator import SignalGenerator

scanner = MarketScanner()
sg = SignalGenerator()

# 获取大盘趋势
market_trend = scanner.get_market_trend()
print(f"大盘趋势: {market_trend}")

# 检查几个股票
test_stocks = ['ADBE-USDT-SWAP', 'HOOD-USDT-SWAP', 'META-USDT-SWAP', 'MSFT-USDT-SWAP']

for symbol in test_stocks:
    data = scanner.data_manager.fetch_klines(symbol, '4H', 100)
    if data is None:
        print(f"{symbol}: 获取数据失败")
        continue
    
    indicators = sg.calculate_indicators(data['prices'], data['volumes'])
    if indicators is None:
        print(f"{symbol}: 计算指标失败")
        continue
    
    signal, score, reasons, strategy_type = sg.generate_signal(indicators, market_trend)
    
    print(f"{symbol}:")
    print(f"  价格: {indicators['current']:.2f}")
    print(f"  MA50: {indicators['sma_50']:.2f}")
    print(f"  RSI: {indicators['rsi']:.1f}")
    print(f"  信号: {signal}")
    print(f"  得分: {score}")
    print(f"  原因: {reasons}")
    print()
