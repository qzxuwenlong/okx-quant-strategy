# -*- coding: utf-8 -*-
"""测试修复后的筛选逻辑"""

import sys
sys.path.insert(0, '.')

from src.core.data_manager import DataManager
from config.settings import PROXY, US_STOCK_KEYWORDS

dm = DataManager(PROXY)

print("=" * 60)
print("测试筛选逻辑")
print("=" * 60)

# 获取所有交易对
all_symbols = dm.get_all_symbols()
print(f"\nOKX总交易对: {len(all_symbols)}")

# 新的筛选逻辑：keyword必须在symbol的开头
us_symbols = []
for symbol in all_symbols:
    if '-USDT-SWAP' not in symbol:
        continue
    
    # 提取股票代码
    stock_code = symbol.replace('-USDT-SWAP', '')
    
    # 检查是否在关键词列表中（精确匹配）
    if stock_code in US_STOCK_KEYWORDS:
        us_symbols.append(symbol)

print(f"精确匹配到 {len(us_symbols)} 个美股")

# 显示
us_symbols.sort()
for i, symbol in enumerate(us_symbols[:50], 1):
    print(f"{i:3}. {symbol}")

if len(us_symbols) > 50:
    print(f"\n... 还有 {len(us_symbols) - 50} 个")

print(f"\n" + "=" * 60)
print(f"总结: 精确匹配到 {len(us_symbols)} 个真正的美股")
print("=" * 60)
