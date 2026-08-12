# -*- coding: utf-8 -*-
"""查询OKX账户状态"""

import sys
sys.path.insert(0, '.')

from src.core.auto_trader import OKXTrader
from config.api_keys import API_KEY, SECRET, PASSPHRASE
from config.settings import PROXY

# 创建交易器
trader = OKXTrader(
    api_key=API_KEY,
    secret=SECRET,
    passphrase=PASSPHRASE,
    sandbox=True,  # 模拟盘
    proxy=PROXY
)

print("=" * 60)
print("OKX账户状态查询")
print("=" * 60)

# 查询余额
print("\n[1] 查询余额...")
balance = trader.get_balance()
if balance:
    print(f"  总余额: {balance.get('total_eq', 'N/A')} USDT")
    print(f"  可用余额: {balance.get('avail_eq', 'N/A')} USDT")
else:
    print("  查询失败")

# 查询持仓
print("\n[2] 查询持仓...")
positions = trader.get_positions()
if positions:
    print(f"  持仓数量: {len(positions)}")
    for pos in positions:
        print(f"\n  交易对: {pos.get('instId', 'N/A')}")
        print(f"  方向: {pos.get('posSide', 'N/A')}")
        print(f"  数量: {pos.get('pos', 'N/A')}")
        print(f"  开仓价: {pos.get('avgPx', 'N/A')}")
        print(f"  当前价: {pos.get('last', 'N/A')}")
        print(f"  未实现盈亏: {pos.get('upl', 'N/A')} USDT")
else:
    print("  无持仓")

print("\n" + "=" * 60)
