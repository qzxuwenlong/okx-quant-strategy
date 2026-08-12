# -*- coding: utf-8 -*-
"""对比昨天和今天的信号差异"""

import sys
sys.path.insert(0, '.')

from src.strategies.scanner import MarketScanner
from src.core.signal_generator import SignalGenerator

scanner = MarketScanner()
sg = SignalGenerator()

print("=" * 60)
print("昨天 vs 今天 信号对比")
print("=" * 60)

# 昨天有信号的股票
yesterday_stocks = ['ADBE', 'HOOD', 'IWM', 'META', 'MSFT', 'NFLX', 'NVDA', 'QQQ', 'QCOM']

for stock in yesterday_stocks:
    symbol = stock + '-USDT-SWAP'
    data = scanner.data_manager.fetch_klines(symbol, '4H', 100)
    if data is None:
        continue
    
    # 昨天数据
    if len(data['prices']) >= 2:
        prices_y = data['prices'][:-1]
        volumes_y = data['volumes'][:-1]
        ind_y = sg.calculate_indicators(prices_y, volumes_y)
        sig_y, score_y, _, _ = sg.generate_signal(ind_y, 'bullish')
    else:
        sig_y = '-'
        ind_y = {'rsi': 0, 'current': 0, 'sma_50': 0}
    
    # 今天数据
    ind_t = sg.calculate_indicators(data['prices'], data['volumes'])
    sig_t, score_t, _, _ = sg.generate_signal(ind_t, 'bullish')
    
    # 对比
    rsi_change = ind_t['rsi'] - ind_y['rsi']
    price_change = ind_t['current'] - ind_y['current']
    
    print(f"{symbol:<20} 昨天:{sig_y:<6} 今天:{sig_t:<6} RSI变化:{rsi_change:+.1f} 价格变化:{price_change:+.2f}")

print("=" * 60)
