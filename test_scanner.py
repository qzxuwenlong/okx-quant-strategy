# -*- coding: utf-8 -*-
"""测试更新后的扫描器"""

import sys
sys.path.insert(0, '.')

from src.strategies.scanner import MarketScanner

scanner = MarketScanner()

print("=" * 60)
print("测试更新后的扫描器")
print("=" * 60)

# 获取美股列表
symbols = scanner.get_us_stock_symbols()
print(f"\n从OKX获取到 {len(symbols)} 个美股交易对")

# 显示前50个
print(f"\n前50个美股:")
for i, symbol in enumerate(symbols[:50], 1):
    print(f"{i:3}. {symbol}")
    
print(f"\n... 还有 {len(symbols) - 50} 个")
print("=" * 60)
