# -*- coding: utf-8 -*-
"""分析为什么没有信号"""

import sys
sys.path.insert(0, '.')

from src.strategies.scanner import MarketScanner
from src.core.signal_generator import SignalGenerator

scanner = MarketScanner()
sg = SignalGenerator()

# 获取大盘趋势
market_trend = scanner.get_market_trend()
print("=" * 60)
print("信号分析")
print("=" * 60)
print(f"\n大盘趋势: {market_trend}")

# 获取已有持仓
from src.core.auto_trader import OKXTrader
from config.api_keys import API_KEY, SECRET, PASSPHRASE
from config.settings import PROXY

trader = OKXTrader(
    api_key=API_KEY,
    secret=SECRET,
    passphrase=PASSPHRASE,
    sandbox=False,
    proxy=PROXY
)

positions = trader.get_positions()
position_symbols = [p['instId'] for p in positions] if positions else []
print(f"\n已有持仓: {position_symbols}")

# 获取所有美股
symbols = scanner.get_us_stock_symbols()
print(f"\n扫描 {len(symbols)} 个美股...")

# 逐个分析
buy_count = 0
short_count = 0
skip_count = 0

for symbol in symbols[:10]:  # 只看前10个
    data = scanner.data_manager.fetch_klines(symbol, '4H', 100)
    if data is None:
        continue
    
    indicators = sg.calculate_indicators(data['prices'], data['volumes'])
    if indicators is None:
        continue
    
    signal, score, reasons, strategy_type = sg.generate_signal(indicators, market_trend)
    
    rsi = indicators['rsi']
    current = indicators['current']
    sma_50 = indicators['sma_50']
    
    status = ""
    if symbol in position_symbols:
        status = "[已有持仓]"
        skip_count += 1
    elif signal == 'buy':
        buy_count += 1
        status = "[买入信号]"
    elif signal == 'short':
        short_count += 1
        status = "[做空信号]"
    else:
        status = "[无信号]"
    
    print(f"{symbol:<20} RSI:{rsi:.1f} 价格:{current:.2f} MA50:{sma_50:.2f} {status}")

print(f"\n" + "=" * 60)
print(f"统计: 买入信号{buy_count}个, 做空信号{short_count}个, 已有持仓{skip_count}个")
print("=" * 60)
