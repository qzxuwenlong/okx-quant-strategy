# -*- coding: utf-8 -*-
"""
市场扫描模块
整合欧奈尔卖空理论
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.data_manager import DataManager
from src.core.signal_generator import SignalGenerator
from config.settings import MIN_SCORE, PROXY, MARKET_FILTER, US_STOCK_KEYWORDS
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class MarketScanner:
    def __init__(self):
        self.data_manager = DataManager(PROXY)
        self.signal_generator = SignalGenerator()
        self.market_trend = 'neutral'
    
    def get_us_stock_symbols(self):
        all_symbols = self.data_manager.get_all_symbols()
        us_symbols = []
        for symbol in all_symbols:
            for keyword in US_STOCK_KEYWORDS:
                if keyword in symbol and 'USDT' in symbol:
                    us_symbols.append(symbol)
                    break
        return sorted(list(set(us_symbols)))
    
    def get_market_trend(self):
        for symbol in ['SPY-USDT-SWAP', 'QQQ-USDT-SWAP']:
            data = self.data_manager.fetch_klines(symbol)
            if data:
                indicators = self.signal_generator.calculate_indicators(data['prices'], data['volumes'])
                if indicators:
                    trend = self.signal_generator.get_market_trend(indicators)
                    print('大盘趋势 (' + symbol + '): ' + trend)
                    return trend
        print('无法获取大盘数据，默认中性')
        return 'neutral'
    
    def get_filtered_symbols(self):
        if MARKET_FILTER == 'us_stocks':
            symbols = self.get_us_stock_symbols()
            print('从OKX获取到 ' + str(len(symbols)) + ' 个美股交易对')
            return symbols
        elif MARKET_FILTER == 'crypto':
            all_symbols = self.data_manager.get_all_symbols()
            us_symbols = set(self.get_us_stock_symbols())
            return [s for s in all_symbols if s not in us_symbols]
        else:
            return self.data_manager.get_all_symbols()
    
    def analyze_symbol(self, symbol):
        data = self.data_manager.fetch_klines(symbol)
        if not data:
            return None
        indicators = self.signal_generator.calculate_indicators(data['prices'], data['volumes'])
        if not indicators:
            return None
        signal, score, reasons = self.signal_generator.generate_signal(indicators, self.market_trend)
        
        if signal in ['buy', 'short'] and score >= MIN_SCORE:
            atr = indicators['atr']
            current = indicators['current']
            if signal == 'buy':
                return {
                    'symbol': symbol,
                    'price': current,
                    'rsi': round(indicators['rsi'], 2),
                    'score': score,
                    'signal': 'buy',
                    'reasons': reasons,
                    'stop_loss': round(current - (atr * 2), 4),
                    'take_profit': round(current + (atr * 4), 4),
                    'risk_reward': '1:2'
                }
            else:
                return {
                    'symbol': symbol,
                    'price': current,
                    'rsi': round(indicators['rsi'], 2),
                    'score': score,
                    'signal': 'short',
                    'reasons': reasons,
                    'stop_loss': round(current + (atr * 2), 4),
                    'take_profit': round(current - (atr * 4), 4),
                    'risk_reward': '1:2'
                }
        return None
    
    def scan(self):
        print('')
        print('=' * 60)
        print('扫描市场...')
        print('品种筛选: ' + MARKET_FILTER)
        print('=' * 60)
        
        self.market_trend = self.get_market_trend()
        symbols = self.get_filtered_symbols()
        print('待扫描交易对: ' + str(len(symbols)) + ' 个')
        
        buy_signals = []
        short_signals = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.analyze_symbol, s): s for s in symbols}
            for i, f in enumerate(as_completed(futures), 1):
                print('  进度: ' + str(i) + '/' + str(len(symbols)))
                try:
                    r = f.result()
                    if r:
                        if r['signal'] == 'buy':
                            buy_signals.append(r)
                        elif r['signal'] == 'short':
                            short_signals.append(r)
                except:
                    pass
        
        buy_signals.sort(key=lambda x: x['score'], reverse=True)
        short_signals.sort(key=lambda x: x['score'], reverse=True)
        
        print('')
        print('做多信号: ' + str(len(buy_signals)) + ' 个')
        print('做空信号: ' + str(len(short_signals)) + ' 个')
        
        return {'buy': buy_signals, 'short': short_signals}
    
    def display(self, results, top_n=20):
        buy_signals = results.get('buy', [])
        short_signals = results.get('short', [])
        
        if not buy_signals and not short_signals:
            print('没有找到信号')
            return
        
        print('')
        print('=' * 120)
        print('OKX美股策略扫描结果 | ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('大盘趋势: ' + self.market_trend.upper())
        print('=' * 120)
        
        # 做多信号
        if buy_signals:
            print('')
            print('=' * 120)
            print('【做多信号 BUY】(' + str(len(buy_signals)) + ' 个)')
            print('=' * 120)
            print('-' * 120)
            header = '{:<3} {:<22} {:<12} {:<8} {:<6} {:<20} {:<12} {:<12} {:<8}'.format(
                '#', '交易对', '价格', 'RSI', '得分', '原因', '止损', '止盈', 'R:R')
            print(header)
            print('-' * 120)
            for i, r in enumerate(buy_signals[:top_n], 1):
                reasons_str = ', '.join(r.get('reasons', [])[:2])
                row = '{:<3} {:<22}  {:<8.1f} {:<6} {:<20}   {:<8}'.format(
                    i, r['symbol'], r['price'], r['rsi'], r['score'], reasons_str,
                    r['stop_loss'], r['take_profit'], r['risk_reward'])
                print(row)
        
        # 做空信号
        if short_signals:
            print('')
            print('=' * 120)
            print('【做空信号 SHORT】(' + str(len(short_signals)) + ' 个) - 欧奈尔卖空')
            print('=' * 120)
            print('-' * 120)
            header = '{:<3} {:<22} {:<12} {:<8} {:<6} {:<25} {:<12} {:<12} {:<8}'.format(
                '#', '交易对', '价格', 'RSI', '得分', '原因', '止损', '止盈', 'R:R')
            print(header)
            print('-' * 120)
            for i, r in enumerate(short_signals[:top_n], 1):
                reasons_str = ', '.join(r.get('reasons', [])[:3])
                row = '{:<3} {:<22}  {:<8.1f} {:<6} {:<25}   {:<8}'.format(
                    i, r['symbol'], r['price'], r['rsi'], r['score'], reasons_str,
                    r['stop_loss'], r['take_profit'], r['risk_reward'])
                print(row)
        
        print('')
        print('=' * 120)
        print('策略说明:')
        print('  做多: 趋势向上(价格>MA50) + RSI适中 + 成交量放大')
        print('  做空: 欧奈尔卖空信号（顶部形态/突破失败/量价背离/RSI反转/均线死叉）')
        print('  大盘过滤: 看多只做多，看空只做空')
        print('  止损: ATR x 2 | 止盈: ATR x 4 | R:R = 1:2')
        print('=' * 120)


if __name__ == '__main__':
    scanner = MarketScanner()
    results = scanner.scan()
    scanner.display(results)
