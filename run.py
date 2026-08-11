# -*- coding: utf-8 -*-
"""
OKX量化策略系统 - 主程序
支持：单次扫描 / 持续监控 / 自动交易
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.strategies.scanner import MarketScanner
from src.core.auto_trader import OKXTrader
from config.settings import API_KEY, SECRET, PASSPHRASE, SANDBOX, PROXY, SCAN_INTERVAL

def run_once(scanner, trader=None):
    """运行一次扫描"""
    results = scanner.scan()
    scanner.display(results)
    
    if trader and API_KEY:
        execute_trades(trader, results)
    
    return results

def run_loop(scanner, trader=None, interval=None):
    """持续运行"""
    interval = interval or SCAN_INTERVAL
    
    print('')
    print('=' * 60)
    print('持续监控模式')
    print('扫描间隔: ' + str(interval) + ' 秒')
    print('按 Ctrl+C 停止')
    print('=' * 60)
    
    cycle = 0
    while True:
        cycle += 1
        print('')
        print('>>> 第 ' + str(cycle) + ' 轮扫描 <<<')
        print('时间: ' + time.strftime('%Y-%m-%d %H:%M:%S'))
        print('-' * 40)
        
        try:
            results = run_once(scanner, trader)
        except Exception as e:
            print('扫描错误: ' + str(e))
        
        print('')
        print('等待 ' + str(interval) + ' 秒...')
        time.sleep(interval)

def execute_trades(trader, results):
    """执行交易"""
    buy_signals = results.get('buy', [])
    
    if not buy_signals:
        return
    
    # 获取当前持仓
    positions = trader.get_positions()
    position_symbols = [p['instId'] for p in positions] if positions else []
    
    # 执行前3个信号
    executed = 0
    for signal in buy_signals[:3]:
        symbol = signal['symbol']
        
        # 跳过已有持仓
        if symbol in position_symbols:
            continue
        
        # 计算仓位大小（100 USDT）
        size = 100 / signal['price']
        
        print('')
        print('下单: ' + symbol)
        print('  价格: $' + str(round(signal['price'], 2)))
        print('  止损: $' + str(round(signal['stop_loss'], 2)))
        print('  止盈: $' + str(round(signal['take_profit'], 2)))
        
        order_id = trader.place_order(
            symbol=symbol,
            side='buy',
            size=round(size, 4),
            stop_loss=signal['stop_loss'],
            take_profit=signal['take_profit']
        )
        
        if order_id:
            executed += 1
    
    if executed > 0:
        print('')
        print('执行完成: ' + str(executed) + ' 笔订单')

def main():
    print('=' * 60)
    print('OKX量化策略系统')
    print('=' * 60)
    print('')
    print('选择模式:')
    print('  1. 单次扫描 - 运行一次')
    print('  2. 持续监控 - 自动循环')
    print('')
    
    choice = input('请选择 (1/2, 默认1): ').strip() or '1'
    
    # 初始化扫描器
    scanner = MarketScanner()
    
    # 初始化交易器（如果有API）
    trader = None
    if API_KEY:
        trader = OKXTrader(
            api_key=API_KEY,
            secret=SECRET,
            passphrase=PASSPHRASE,
            sandbox=SANDBOX,
            proxy=PROXY
        )
        print('API已配置')
    else:
        print('提示: 未配置API，仅扫描信号')
    
    if choice == '2':
        # 持续监控
        interval = input('扫描间隔(秒, 默认' + str(SCAN_INTERVAL) + '): ').strip()
        interval = int(interval) if interval else SCAN_INTERVAL
        run_loop(scanner, trader, interval)
    else:
        # 单次扫描
        run_once(scanner, trader)

if __name__ == '__main__':
    main()
