# -*- coding: utf-8 -*-
"""
OKX实时告警系统
"""

import requests
import time
from datetime import datetime

class AlertSystem:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.alerts = []
        self.alert_history = []
        self.last_alert_time = {}
        self.config = {'cooldown': 300}
    
    def fetch_klines(self, symbol, bar='4H', limit=50):
        try:
            url = "https://www.okx.com/api/v5/market/candles"
            params = {"instId": symbol, "bar": bar, "limit": str(limit)}
            response = requests.get(url, params=params, proxies=self.proxies, timeout=10)
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                rows = data['data']
                return {
                    'prices': [float(row[4]) for row in rows][::-1],
                    'volumes': [float(row[5]) for row in rows][::-1]
                }
        except:
            pass
        return None
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return None
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def generate_signal(self, symbol):
        data = self.fetch_klines(symbol, '4H', 50)
        if not data:
            return None
        
        prices = data['prices']
        volumes = data['volumes']
        current = prices[-1]
        
        sma_20 = sum(prices[-20:]) / 20
        sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
        rsi = self.calculate_rsi(prices)
        
        vol_sma = sum(volumes[-20:]) / 20
        vol_ratio = volumes[-1] / vol_sma if vol_sma > 0 else 0
        
        # ATR
        highs = [max(prices[i], prices[i-1]) for i in range(1, len(prices))]
        lows = [min(prices[i], prices[i-1]) for i in range(1, len(prices))]
        trs = [h - l for h, l in zip(highs[-14:], lows[-14:])]
        atr = sum(trs) / len(trs) if trs else 0
        
        # 得分
        score = 0
        if current > sma_20 and current > sma_50:
            score += 3
        elif current > sma_50:
            score += 2
        
        if rsi and rsi < 30:
            score += 2
        elif rsi and rsi < 45:
            score += 2
        elif rsi and rsi < 65:
            score += 1
        
        if vol_ratio > 1.5:
            score += 2
        elif vol_ratio > 1.2:
            score += 1
        
        if current > sma_50 and (rsi and rsi > 50):
            phase = 'markup'
        elif current < sma_50 and (rsi and rsi < 50):
            phase = 'markdown'
        else:
            phase = 'neutral'
        
        signal = 'hold'
        if score >= 6 and phase == 'markup' and (rsi and 30 < rsi < 70):
            signal = 'strong_buy'
        elif score >= 5 and phase == 'markup' and (rsi and rsi < 65):
            signal = 'buy'
        elif phase == 'markdown' and (rsi and rsi > 65):
            signal = 'short'
        
        stop_loss = None
        take_profit = None
        if signal in ['strong_buy', 'buy']:
            stop_loss = current - (atr * 2)
            take_profit = current + (atr * 4)
        elif signal == 'short':
            stop_loss = current + (atr * 2)
            take_profit = current - (atr * 4)
        
        return {
            'symbol': symbol,
            'price': current,
            'rsi': round(rsi, 2) if rsi else None,
            'phase': phase,
            'signal': signal,
            'score': score,
            'vol_ratio': round(vol_ratio, 2),
            'stop_loss': round(stop_loss, 4) if stop_loss else None,
            'take_profit': round(take_profit, 4) if take_profit else None
        }
    
    def check_alerts(self, symbol):
        alerts = []
        now = time.time()
        
        last_alert = self.last_alert_time.get(symbol, 0)
        if now - last_alert < self.config['cooldown']:
            return alerts
        
        signal_data = self.generate_signal(symbol)
        if not signal_data:
            return alerts
        
        # 信号告警
        if signal_data['signal'] in ['strong_buy', 'buy']:
            alerts.append({
                'type': 'SIGNAL',
                'level': 'HIGH' if signal_data['signal'] == 'strong_buy' else 'MEDIUM',
                'symbol': symbol,
                'message': '买入信号: ' + signal_data['signal'].upper(),
                'price': signal_data['price'],
                'rsi': signal_data['rsi'],
                'score': signal_data['score'],
                'stop_loss': signal_data['stop_loss'],
                'take_profit': signal_data['take_profit'],
                'timestamp': datetime.now()
            })
        elif signal_data['signal'] == 'short':
            alerts.append({
                'type': 'SIGNAL',
                'level': 'HIGH',
                'symbol': symbol,
                'message': '做空信号',
                'price': signal_data['price'],
                'rsi': signal_data['rsi'],
                'timestamp': datetime.now()
            })
        
        # RSI告警
        if signal_data['rsi']:
            if signal_data['rsi'] > 75:
                alerts.append({
                    'type': 'RSI',
                    'level': 'WARNING',
                    'symbol': symbol,
                    'message': 'RSI超买: ' + str(signal_data['rsi']),
                    'price': signal_data['price'],
                    'timestamp': datetime.now()
                })
            elif signal_data['rsi'] < 25:
                alerts.append({
                    'type': 'RSI',
                    'level': 'WARNING',
                    'symbol': symbol,
                    'message': 'RSI超卖: ' + str(signal_data['rsi']),
                    'price': signal_data['price'],
                    'timestamp': datetime.now()
                })
        
        if alerts:
            self.last_alert_time[symbol] = now
            self.alerts.extend(alerts)
            self.alert_history.extend(alerts)
        
        return alerts
    
    def format_alert(self, alert):
        level_map = {
            'CRITICAL': '[CRITICAL]',
            'HIGH': '[HIGH]',
            'MEDIUM': '[MEDIUM]',
            'WARNING': '[WARNING]',
            'INFO': '[INFO]'
        }
        
        level_str = level_map.get(alert['level'], '[INFO]')
        
        lines = []
        lines.append(level_str + " " + alert['type'] + " | " + alert['symbol'])
        lines.append("   " + alert['message'])
        lines.append("   Price: $" + str(round(alert['price'], 2)))
        
        if alert.get('rsi'):
            lines.append("   RSI: " + str(alert['rsi']))
        if alert.get('score'):
            lines.append("   Score: " + str(alert['score']))
        if alert.get('stop_loss'):
            lines.append("   Stop Loss: $" + str(round(alert['stop_loss'], 2)))
        if alert.get('take_profit'):
            lines.append("   Take Profit: $" + str(round(alert['take_profit'], 2)))
        
        lines.append("   Time: " + str(alert['timestamp'])[:19])
        
        return '\n'.join(lines)
    
    def monitor(self, symbols, duration_minutes=60, interval_seconds=300):
        print("=" * 60)
        print("OKX Alert System Started")
        print("=" * 60)
        print("Symbols: " + ', '.join(symbols))
        print("Duration: " + str(duration_minutes) + " min")
        print("Interval: " + str(interval_seconds) + " sec")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        cycle = 0
        while time.time() < end_time:
            cycle += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print("\n[" + timestamp + "] Cycle " + str(cycle))
            print("-" * 40)
            
            all_alerts = []
            
            for symbol in symbols:
                alerts = self.check_alerts(symbol)
                all_alerts.extend(alerts)
                
                signal_data = self.generate_signal(symbol)
                if signal_data:
                    status = symbol.ljust(20) + " $" + str(round(signal_data['price'], 2)).ljust(10)
                    status += " RSI:" + str(signal_data['rsi'] or '-').ljust(6)
                    status += " " + signal_data['phase'].ljust(10)
                    status += " Signal:" + signal_data['signal']
                    print("  " + status)
            
            if all_alerts:
                print("\n" + "!" * 40)
                print("ALERTS!")
                print("!" * 40)
                for alert in all_alerts:
                    print(self.format_alert(alert))
                    print("")
            else:
                print("\n  No alerts")
            
            remaining = int((end_time - time.time()) / 60)
            print("\nWaiting " + str(interval_seconds) + "s... (" + str(remaining) + " min remaining)")
            time.sleep(interval_seconds)
        
        print("\n" + "=" * 60)
        print("Monitor finished")
        print("Total alerts: " + str(len(self.alert_history)))
        print("=" * 60)
        
        return self.alert_history


if __name__ == "__main__":
    print("=" * 60)
    print("OKX Alert System")
    print("=" * 60)
    
    proxy = "http://127.0.0.1:7890"
    alert_system = AlertSystem(proxy=proxy)
    
    symbols = ['TSLA-USDT-SWAP', 'AMZN-USDT-SWAP', 'BTC-USDT-SWAP']
    
    print("\nWatchlist:")
    for s in symbols:
        print("  - " + s)
    
    print("\nStarting monitor (5 min, check every 60s)...")
    print("=" * 60)
    
    alerts = alert_system.monitor(symbols, duration_minutes=5, interval_seconds=60)
    
    if alerts:
        print("\n" + "=" * 60)
        print("Alert History")
        print("=" * 60)
        for alert in alerts:
            print(alert['timestamp'].strftime('%H:%M:%S') + " | " + 
                  alert['type'].ljust(12) + " | " + 
                  alert['symbol'].ljust(20) + " | " + 
                  alert['message'])
