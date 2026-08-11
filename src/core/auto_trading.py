# -*- coding: utf-8 -*-
"""
OKX自动交易系统 - 完整版
集成：扫描 + 信号 + 仓位 + 告警 + 日志 + 自动执行
"""

import requests
import numpy as np
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============== 配置 ==============
CONFIG = {
    'proxy': 'http://127.0.0.1:7890',
    'initial_capital': 10000,
    'risk_per_trade': 0.02,      # 单笔风险2%
    'max_positions': 5,          # 最大持仓数
    'scan_interval': 300,        # 扫描间隔（秒）
    'min_score': 4,              # 最低信号得分
    'enable_auto_trade': False,  # 是否自动交易（需要API）
    'api_key': '',
    'secret': '',
    'passphrase': ''
}

# ============== 数据获取 ==============
class DataManager:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
    
    def fetch_klines(self, symbol, bar='4H', limit=200):
        try:
            url = "https://www.okx.com/api/v5/market/candles"
            params = {"instId": symbol, "bar": bar, "limit": str(limit)}
            response = requests.get(url, params=params, proxies=self.proxies, timeout=10)
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                rows = data['data']
                prices = [float(row[4]) for row in rows][::-1]
                volumes = [float(row[5]) for row in rows][::-1]
                return {'prices': prices, 'volumes': volumes}
        except:
            pass
        return None
    
    def get_all_symbols(self):
        try:
            url = "https://www.okx.com/api/v5/public/instruments"
            params = {"instType": "SWAP"}
            response = requests.get(url, params=params, proxies=self.proxies, timeout=30)
            data = response.json()
            
            if data.get('code') == '0':
                return [inst['instId'] for inst in data['data'] 
                       if inst.get('settleCcy') == 'USDT' and inst.get('state') == 'live']
        except:
            pass
        return []

# ============== 信号生成 ==============
class SignalGenerator:
    def calculate_indicators(self, prices, volumes):
        if len(prices) < 50:
            return None
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        deltas = np.diff(prices[-15:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        vol_sma = np.mean(volumes[-20:])
        vol_ratio = volumes[-1] / vol_sma if vol_sma > 0 else 0
        
        highs = [max(prices[i], prices[i-1]) for i in range(1, len(prices))]
        lows = [min(prices[i], prices[i-1]) for i in range(1, len(prices))]
        trs = [h - l for h, l in zip(highs[-14:], lows[-14:])]
        atr = np.mean(trs)
        
        return {
            'current': prices[-1],
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'vol_ratio': vol_ratio,
            'atr': atr
        }
    
    def generate_signal(self, indicators):
        if not indicators:
            return 'hold', 0
        
        current = indicators['current']
        sma_50 = indicators['sma_50']
        rsi = indicators['rsi']
        vol_ratio = indicators['vol_ratio']
        
        score = 0
        
        if current > sma_50:
            score += 3
        
        if rsi < 30:
            score += 2
        elif rsi < 45:
            score += 2
        elif rsi < 65:
            score += 1
        
        if vol_ratio > 1.2:
            score += 1
        
        if score >= 5 and 30 < rsi < 70:
            return 'buy', score
        elif score >= 4 and rsi < 65:
            return 'buy', score
        
        return 'hold', score

# ============== 仓位管理 ==============
class PositionManager:
    def __init__(self, capital, risk_per_trade, max_positions):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.positions = {}
    
    def calculate_size(self, entry_price, stop_loss):
        risk_amount = self.capital * self.risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit <= 0:
            return 0
        
        position_size = risk_amount / risk_per_unit
        position_value = position_size * entry_price
        
        max_value = self.capital * 0.20
        if position_value > max_value:
            position_size = max_value / entry_price
        
        return round(position_size, 4)
    
    def can_open(self):
        return len(self.positions) < self.max_positions
    
    def add_position(self, symbol, entry_price, size, stop_loss, take_profit, signal_type='long'):
        self.positions[symbol] = {
            'entry_price': entry_price,
            'size': size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'type': signal_type,
            'entry_time': datetime.now(),
            'unrealized_pnl': 0
        }
    
    def remove_position(self, symbol):
        if symbol in self.positions:
            del self.positions[symbol]
    
    def update_pnl(self, symbol, current_price):
        if symbol in self.positions:
            pos = self.positions[symbol]
            if pos['type'] == 'long':
                pos['unrealized_pnl'] = (current_price - pos['entry_price']) * pos['size']
            else:
                pos['unrealized_pnl'] = (pos['entry_price'] - current_price) * pos['size']
    
    def check_exits(self, symbol, current_price, rsi):
        if symbol not in self.positions:
            return None, None
        
        pos = self.positions[symbol]
        
        if pos['type'] == 'long':
            if current_price <= pos['stop_loss']:
                return '止损', current_price
            elif current_price >= pos['take_profit']:
                return '止盈', current_price
            elif rsi > 75:
                return 'RSI超买', current_price
        else:
            if current_price >= pos['stop_loss']:
                return '止损', current_price
            elif current_price <= pos['take_profit']:
                return '止盈', current_price
            elif rsi < 25:
                return 'RSI超卖', current_price
        
        return None, None
    
    def get_summary(self):
        total_value = sum(p['entry_price'] * p['size'] for p in self.positions.values())
        total_pnl = sum(p['unrealized_pnl'] for p in self.positions.values())
        
        return {
            'positions': len(self.positions),
            'total_value': round(total_value, 2),
            'total_pnl': round(total_pnl, 2),
            'available': round(self.capital - total_value, 2)
        }

# ============== 交易日志 ==============
class TradeJournal:
    def __init__(self, log_file='auto_trades.json'):
        self.log_file = log_file
        self.trades = []
        self.load()
    
    def load(self):
        try:
            with open(self.log_file, 'r') as f:
                self.trades = json.load(f)
        except:
            self.trades = []
    
    def save(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.trades, f, default=str)
    
    def add_trade(self, trade):
        trade['id'] = len(self.trades) + 1
        trade['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.trades.append(trade)
        self.save()
    
    def get_stats(self):
        if not self.trades:
            return {'total': 0, 'wins': 0, 'losses': 0, 'win_rate': 0, 'total_pnl': 0}
        
        wins = [t for t in self.trades if t.get('pnl', 0) > 0]
        losses = [t for t in self.trades if t.get('pnl', 0) <= 0]
        
        return {
            'total': len(self.trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(len(wins) / len(self.trades) * 100, 1) if self.trades else 0,
            'total_pnl': round(sum(t.get('pnl', 0) for t in self.trades), 2)
        }

# ============== 告警系统 ==============
class AlertSystem:
    def __init__(self):
        self.alerts = []
        self.last_alert = {}
    
    def should_alert(self, symbol, alert_type):
        key = symbol + '_' + alert_type
        last_time = self.last_alert.get(key, 0)
        if time.time() - last_time < 300:  # 5分钟冷却
            return False
        self.last_alert[key] = time.time()
        return True
    
    def add_alert(self, symbol, alert_type, message, data=None):
        if self.should_alert(symbol, alert_type):
            alert = {
                'symbol': symbol,
                'type': alert_type,
                'message': message,
                'data': data,
                'time': datetime.now().strftime('%H:%M:%S')
            }
            self.alerts.append(alert)
            return alert
        return None
    
    def format_alert(self, alert):
        return "[" + alert['time'] + "] " + alert['type'] + " | " + alert['symbol'] + " | " + alert['message']

# ============== 主系统 ==============
class AutoTradingSystem:
    def __init__(self, config):
        self.config = config
        self.data_manager = DataManager(config['proxy'])
        self.signal_generator = SignalGenerator()
        self.position_manager = PositionManager(
            config['initial_capital'],
            config['risk_per_trade'],
            config['max_positions']
        )
        self.journal = TradeJournal()
        self.alert_system = AlertSystem()
        self.running = False
    
    def scan_market(self):
        """扫描市场"""
        print("\n" + "=" * 60)
        print("扫描市场...")
        print("=" * 60)
        
        symbols = self.data_manager.get_all_symbols()
        print("交易对数量: " + str(len(symbols)))
        
        results = []
        
        def analyze(symbol):
            data = self.data_manager.fetch_klines(symbol)
            if not data:
                return None
            
            indicators = self.signal_generator.calculate_indicators(data['prices'], data['volumes'])
            if not indicators:
                return None
            
            signal, score = self.signal_generator.generate_signal(indicators)
            
            if signal == 'buy' and score >= self.config['min_score']:
                atr = indicators['atr']
                current = indicators['current']
                
                return {
                    'symbol': symbol,
                    'price': current,
                    'rsi': round(indicators['rsi'], 2),
                    'vol_ratio': round(indicators['vol_ratio'], 2),
                    'score': score,
                    'stop_loss': round(current - (atr * 2), 4),
                    'take_profit': round(current + (atr * 4), 4)
                }
            return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(analyze, s): s for s in symbols}
            
            for i, f in enumerate(as_completed(futures), 1):
                if i % 100 == 0:
                    print("  进度: " + str(i) + "/" + str(len(symbols)))
                try:
                    r = f.result()
                    if r:
                        results.append(r)
                except:
                    pass
        
        results.sort(key=lambda x: x['score'], reverse=True)
        print("找到信号: " + str(len(results)) + " 个")
        
        return results
    
    def check_positions(self):
        """检查持仓"""
        exits = []
        
        for symbol in list(self.position_manager.positions.keys()):
            data = self.data_manager.fetch_klines(symbol, '4H', 20)
            if not data:
                continue
            
            indicators = self.signal_generator.calculate_indicators(data['prices'], data['volumes'])
            if not indicators:
                continue
            
            current = indicators['current']
            rsi = indicators['rsi']
            
            self.position_manager.update_pnl(symbol, current)
            
            exit_reason, exit_price = self.position_manager.check_exits(symbol, current, rsi)
            
            if exit_reason:
                pos = self.position_manager.positions[symbol]
                pnl = (exit_price - pos['entry_price']) * pos['size'] if pos['type'] == 'long' else (pos['entry_price'] - exit_price) * pos['size']
                
                exits.append({
                    'symbol': symbol,
                    'reason': exit_reason,
                    'entry': pos['entry_price'],
                    'exit': exit_price,
                    'pnl': round(pnl, 2),
                    'pnl_pct': round(pnl / (pos['entry_price'] * pos['size']) * 100, 2)
                })
                
                # 记录交易
                self.journal.add_trade({
                    'symbol': symbol,
                    'type': pos['type'],
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'size': pos['size'],
                    'pnl': round(pnl, 2),
                    'reason': exit_reason
                })
                
                # 告警
                self.alert_system.add_alert(symbol, 'EXIT', exit_reason + ' | PnL: $' + str(round(pnl, 2)))
                
                # 移除持仓
                self.position_manager.remove_position(symbol)
        
        return exits
    
    def execute_signals(self, signals):
        """执行信号"""
        executed = []
        
        for signal in signals:
            symbol = signal['symbol']
            
            # 检查是否已有持仓
            if symbol in self.position_manager.positions:
                continue
            
            # 检查是否可以开仓
            if not self.position_manager.can_open():
                break
            
            # 计算仓位
            size = self.position_manager.calculate_size(signal['price'], signal['stop_loss'])
            
            if size <= 0:
                continue
            
            # 开仓
            self.position_manager.add_position(
                symbol,
                signal['price'],
                size,
                signal['stop_loss'],
                signal['take_profit'],
                'long'
            )
            
            # 告警
            self.alert_system.add_alert(symbol, 'BUY', 
                '买入 | 价格: $' + str(round(signal['price'], 2)) + 
                ' | 止损: $' + str(round(signal['stop_loss'], 2)) +
                ' | 止盈: $' + str(round(signal['take_profit'], 2)))
            
            executed.append(signal)
        
        return executed
    
    def display_status(self, signals=None, exits=None, executed=None):
        """显示状态"""
        print("\n" + "=" * 60)
        print("系统状态 | " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 60)
        
        # 持仓状态
        summary = self.position_manager.get_summary()
        print("\n[持仓]")
        print("  持仓数: " + str(summary['positions']) + "/" + str(self.config['max_positions']))
        print("  持仓价值: $" + str(summary['total_value']))
        print("  浮动盈亏: $" + str(summary['total_pnl']))
        print("  可用资金: $" + str(summary['available']))
        
        # 持仓详情
        if self.position_manager.positions:
            print("\n  交易对                    入场价        当前盈亏")
            print("  " + "-" * 50)
            for symbol, pos in self.position_manager.positions.items():
                pnl_str = "+$" + str(round(pos['unrealized_pnl'], 2)) if pos['unrealized_pnl'] >= 0 else "-$" + str(abs(round(pos['unrealized_pnl'], 2)))
                print("  " + symbol.ljust(25) + "$" + str(round(pos['entry_price'], 2)).ljust(12) + pnl_str)
        
        # 交易统计
        stats = self.journal.get_stats()
        print("\n[交易统计]")
        print("  总交易: " + str(stats['total']))
        print("  胜率: " + str(stats['win_rate']) + "%")
        print("  总盈亏: $" + str(stats['total_pnl']))
        
        # 今日信号
        if signals:
            print("\n[今日信号] TOP 5")
            for i, s in enumerate(signals[:5], 1):
                print("  " + str(i) + ". " + s['symbol'].ljust(20) + 
                      " $" + str(round(s['price'], 2)).ljust(10) + 
                      " RSI:" + str(s['rsi']).ljust(6) + 
                      " 得分:" + str(s['score']))
        
        # 今日出场
        if exits:
            print("\n[今日出场]")
            for e in exits:
                pnl_str = "+$" + str(e['pnl']) if e['pnl'] >= 0 else "-$" + str(abs(e['pnl']))
                print("  " + e['symbol'].ljust(20) + e['reason'].ljust(10) + pnl_str)
        
        # 今日开仓
        if executed:
            print("\n[今日开仓]")
            for e in executed:
                print("  " + e['symbol'].ljust(20) + 
                      " $" + str(round(e['price'], 2)) + 
                      " 止损:$" + str(round(e['stop_loss'], 2)))
        
        # 告警
        if self.alert_system.alerts:
            print("\n[最近告警]")
            for alert in self.alert_system.alerts[-5:]:
                print("  " + self.alert_system.format_alert(alert))
    
    def run_once(self):
        """运行一次"""
        # 1. 扫描市场
        signals = self.scan_market()
        
        # 2. 检查持仓出场
        exits = self.check_positions()
        
        # 3. 执行新信号
        executed = self.execute_signals(signals)
        
        # 4. 显示状态
        self.display_status(signals, exits, executed)
        
        return signals, exits, executed
    
    def run_loop(self):
        """持续运行"""
        self.running = True
        
        print("=" * 60)
        print("OKX自动交易系统启动")
        print("=" * 60)
        print("扫描间隔: " + str(self.config['scan_interval']) + " 秒")
        print("最低得分: " + str(self.config['min_score']))
        print("最大持仓: " + str(self.config['max_positions']))
        print("单笔风险: " + str(self.config['risk_per_trade'] * 100) + "%")
        print("=" * 60)
        
        cycle = 0
        while self.running:
            cycle += 1
            print("\n\n>>> 第 " + str(cycle) + " 轮 <<<")
            
            try:
                self.run_once()
            except Exception as e:
                print("错误: " + str(e))
            
            print("\n等待 " + str(self.config['scan_interval']) + " 秒...")
            time.sleep(self.config['scan_interval'])
    
    def stop(self):
        """停止系统"""
        self.running = False
        print("\n系统停止")


# ============== 入口 ==============
def main():
    print("=" * 60)
    print("OKX自动交易系统")
    print("=" * 60)
    print("")
    print("功能:")
    print("  1. 市场扫描 - 找出符合条件的交易对")
    print("  2. 信号生成 - 自动生成买卖信号")
    print("  3. 仓位管理 - 自动计算仓位大小")
    print("  4. 止盈止损 - 自动监控出场条件")
    print("  5. 实时告警 - 信号和出场通知")
    print("  6. 交易日志 - 记录所有交易")
    print("")
    print("选择模式:")
    print("  1. 单次扫描（查看信号）")
    print("  2. 持续监控（自动运行）")
    print("")
    
    choice = input("请选择 (1/2): ").strip() or '1'
    
    system = AutoTradingSystem(CONFIG)
    
    if choice == '1':
        system.run_once()
    else:
        system.run_loop()


if __name__ == "__main__":
    main()
