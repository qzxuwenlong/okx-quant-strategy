# -*- coding: utf-8 -*-
"""查看OKX上所有可用的美股交易对"""

import sys
sys.path.insert(0, '.')

from src.core.data_manager import DataManager
from config.settings import PROXY

dm = DataManager(PROXY)

print("=" * 60)
print("OKX上的美股永续合约")
print("=" * 60)

# 获取所有交易对
all_symbols = dm.get_all_symbols()

# 筛选美股（通常以-USDT-SWAP结尾，且是知名公司）
us_stocks = []
for symbol in all_symbols:
    if '-USDT-SWAP' in symbol:
        # 检查是否是美股（排除加密货币）
        stock_name = symbol.replace('-USDT-SWAP', '')
        # 简单判断：如果不是常见的加密货币，可能是美股
        crypto_keywords = ['BTC', 'ETH', 'SOL', 'DOGE', 'SHIB', 'PEPE', 'XRP', 'ADA', 'DOT', 'LINK', 'UNI', 'AAVE']
        is_crypto = any(crypto in stock_name for crypto in crypto_keywords)
        
        if not is_crypto and len(stock_name) <= 5:  # 股票代码通常5个字符以内
            us_stocks.append(symbol)

print(f"\n找到 {len(us_stocks)} 个可能的美股永续合约:\n")

# 按字母排序
us_stocks.sort()

# 显示
for i, stock in enumerate(us_stocks, 1):
    print(f"{i:3}. {stock}")
    
print(f"\n" + "=" * 60)
print(f"总共 {len(us_stocks)} 个美股永续合约")
print("=" * 60)
