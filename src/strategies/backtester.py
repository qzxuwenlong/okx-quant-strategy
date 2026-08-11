# -*- coding: utf-8 -*-
"""
OKX策略回测系统
验证欧奈尔+威科夫策略的历史表现
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

class Backtester:
    """回测系统"""
    
    def __init__(self, initial_capital=10000, risk_per_trade=0.02, max_positions=5):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        
        self.trades = []
        self.open_positions = []
        self.equity_curve = []
        
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0
        self.max_drawdown = 0
        self.peak_equity = initial_capital
    
    def fetch_data(self, symbol, bar='4H', limit=300, proxy=None):
        """获取K线数据"""
        try:
            proxies = {"http": proxy, "https": proxy} if proxy else None
            url = "https://www.okx.com/api/v5/market/candles"
            params = {"instId": symbol, "bar": bar, "limit": str(limit)}
            
            response = requests.get(url, params=params, proxies=proxies, timeout=15)
            data = response.json()
            
            if data.get('code') != '0' or not data.get('data'):
                return None
            
            rows = data['data']
            # OKX返回格式: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            prices = []
            for row in rows:
                prices.append({
                    'timestamp': int(row[0]),
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4]),
                    'vol': float(row[5])
                })
            
            df = pd.DataFrame(prices)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        
        except Exception as e:
            print("获取数据失败: " + str(e))
            return None
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 移动平均
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1)))
        )
        df['atr'] = df['tr'].rolling(14).mean()
        
        # 成交量
        df['vol_sma'] = df['vol'].rolling(20).mean()
        df['vol_ratio'] = df['vol'] / df['vol_sma']
        
        return df
    
    def generate_signal(self, row):
        """生成交易信号"""
        if pd.isna(row['sma_50']) or pd.isna(row['rsi']):
            return 'hold', 0
        
        current = row['close']
        sma_20 = row['sma_20']
        sma_50 = row['sma_50']
        rsi = row['rsi']
        vol_ratio = row['vol_ratio']
        
        # 得分计算
        score = 0
        
        if current > sma_20 and current > sma_50:
            score += 3
        elif current > sma_50:
            score += 2
        
        if rsi < 30:
            score += 2
        elif rsi < 45:
            score += 2
        elif rsi < 65:
            score += 1
        
        if vol_ratio > 1.5:
            score += 2
        elif vol_ratio > 1.2:
            score += 1
        
        # 阶段判断
        if current > sma_50 and rsi > 50:
            phase = 'markup'
        elif current < sma_50 and rsi < 50:
            phase = 'markdown'
        else:
            phase = 'neutral'
        
        # 信号生成
        if score >= 6 and phase == 'markup' and 30 < rsi < 70:
            return 'strong_buy', score
        elif score >= 5 and phase in ['markup'] and rsi < 65:
            return 'buy', score
        elif phase == 'markdown' and rsi > 65:
            return 'short', score
        
        return 'hold', score
    
    def calculate_position_size(self, entry_price, stop_loss):
        """计算仓位大小"""
        risk_amount = self.capital * self.risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit <= 0:
            return 0
        
        position_size = risk_amount / risk_per_unit
        position_value = position_size * entry_price
        
        # 检查上限（20%）
        max_value = self.capital * 0.20
        if position_value > max_value:
            position_size = max_value / entry_price
        
        return round(position_size, 4)
    
    def run_backtest(self, symbol, proxy=None):
        """运行回测"""
        print("=" * 60)
        print("回测: " + symbol)
        print("=" * 60)
        
        # 获取数据（4小时K线，300根 ≈ 50天）
        df = self.fetch_data(symbol, '4H', 300, proxy)
        if df is None or len(df) < 60:
            print("数据不足")
            return None
        
        print("K线数量: " + str(len(df)))
        print("时间: " + str(df['timestamp'].iloc[0])[:10] + " ~ " + str(df['timestamp'].iloc[-1])[:10])
        
        # 计算指标
        df = self.calculate_indicators(df)
        
        # 重置
        self.capital = self.initial_capital
        self.trades = []
        self.open_positions = []
        self.equity_curve = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0
        self.max_drawdown = 0
        self.peak_equity = self.initial_capital
        
        # 回测循环
        for i in range(50, len(df)):
            row = df.iloc[i]
            
            # 更新持仓盈亏
            self.update_positions(row)
            
            # 检查出场
            self.check_exits(row)
            
            # 生成信号
            signal, score = self.generate_signal(row)
            
            # 执行交易
            if signal in ['strong_buy', 'buy'] and len(self.open_positions) < self.max_positions:
                self.open_trade(row, signal, score)
            elif signal == 'short' and len(self.open_positions) < self.max_positions:
                self.open_trade(row, signal, score)
            
            # 记录权益
            total_equity = self.capital + sum(p.get('unrealized_pnl', 0) for p in self.open_positions)
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'equity': total_equity
            })
            
            # 更新最大回撤
            if total_equity > self.peak_equity:
                self.peak_equity = total_equity
            drawdown = (self.peak_equity - total_equity) / self.peak_equity
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
        
        # 平仓所有持仓
        if self.open_positions:
            self.close_all_positions(df.iloc[-1])
        
        # 计算绩效
        results = self.calculate_performance(symbol)
        
        return results
    
    def open_trade(self, row, signal, score):
        """开仓"""
        current = row['close']
        atr = row['atr']
        
        if pd.isna(atr) or atr <= 0:
            return
        
        # 计算止损止盈
        if signal in ['strong_buy', 'buy']:
            stop_loss = current - (atr * 2)
            take_profit = current + (atr * 4)
            trade_type = 'long'
        else:
            stop_loss = current + (atr * 2)
            take_profit = current - (atr * 4)
            trade_type = 'short'
        
        # 计算仓位
        position_size = self.calculate_position_size(current, stop_loss)
        
        if position_size <= 0:
            return
        
        trade = {
            'entry_time': row['timestamp'],
            'entry_price': current,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size': position_size,
            'type': trade_type,
            'signal': signal,
            'score': score,
            'unrealized_pnl': 0
        }
        
        self.open_positions.append(trade)
    
    def update_positions(self, row):
        """更新持仓盈亏"""
        current = row['close']
        
        for pos in self.open_positions:
            if pos['type'] == 'long':
                pos['unrealized_pnl'] = (current - pos['entry_price']) * pos['size']
            else:
                pos['unrealized_pnl'] = (pos['entry_price'] - current) * pos['size']
    
    def check_exits(self, row):
        """检查出场条件"""
        current = row['close']
        rsi = row['rsi'] if not pd.isna(row['rsi']) else 50
        closed = []
        
        for i, pos in enumerate(self.open_positions):
            should_close = False
            exit_reason = ''
            exit_price = current
            
            # 止损
            if pos['type'] == 'long' and current <= pos['stop_loss']:
                should_close = True
                exit_reason = '止损'
                exit_price = pos['stop_loss']
            elif pos['type'] == 'short' and current >= pos['stop_loss']:
                should_close = True
                exit_reason = '止损'
                exit_price = pos['stop_loss']
            
            # 止盈
            elif pos['type'] == 'long' and current >= pos['take_profit']:
                should_close = True
                exit_reason = '止盈'
                exit_price = pos['take_profit']
            elif pos['type'] == 'short' and current <= pos['take_profit']:
                should_close = True
                exit_reason = '止盈'
                exit_price = pos['take_profit']
            
            # RSI出场
            elif pos['type'] == 'long' and rsi > 75:
                should_close = True
                exit_reason = 'RSI超买'
            elif pos['type'] == 'short' and rsi < 25:
                should_close = True
                exit_reason = 'RSI超卖'
            
            if should_close:
                if pos['type'] == 'long':
                    pnl = (exit_price - pos['entry_price']) * pos['size']
                else:
                    pnl = (pos['entry_price'] - exit_price) * pos['size']
                
                entry_val = pos['entry_price'] * pos['size']
                pnl_pct = pnl / entry_val * 100 if entry_val > 0 else 0
                
                trade_record = {
                    'entry_time': pos['entry_time'],
                    'exit_time': row['timestamp'],
                    'entry_price': round(pos['entry_price'], 4),
                    'exit_price': round(exit_price, 4),
                    'size': pos['size'],
                    'type': pos['type'],
                    'signal': pos['signal'],
                    'pnl': round(pnl, 2),
                    'pnl_pct': round(pnl_pct, 2),
                    'exit_reason': exit_reason
                }
                
                self.trades.append(trade_record)
                self.capital += pnl
                self.total_pnl += pnl
                
                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                
                self.total_trades += 1
                closed.append(i)
        
        for i in sorted(closed, reverse=True):
            self.open_positions.pop(i)
    
    def close_all_positions(self, row):
        """平仓所有持仓"""
        current = row['close']
        
        for pos in self.open_positions:
            if pos['type'] == 'long':
                pnl = (current - pos['entry_price']) * pos['size']
            else:
                pnl = (pos['entry_price'] - current) * pos['size']
            
            entry_val = pos['entry_price'] * pos['size']
            pnl_pct = pnl / entry_val * 100 if entry_val > 0 else 0
            
            trade_record = {
                'entry_time': pos['entry_time'],
                'exit_time': row['timestamp'],
                'entry_price': round(pos['entry_price'], 4),
                'exit_price': round(current, 4),
                'size': pos['size'],
                'type': pos['type'],
                'signal': pos['signal'],
                'pnl': round(pnl, 2),
                'pnl_pct': round(pnl_pct, 2),
                'exit_reason': '回测结束'
            }
            
            self.trades.append(trade_record)
            self.capital += pnl
            self.total_pnl += pnl
            
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            self.total_trades += 1
        
        self.open_positions = []
    
    def calculate_performance(self, symbol=''):
        """计算绩效指标"""
        if not self.trades:
            return None
        
        win_rate = self.winning_trades / self.total_trades * 100 if self.total_trades > 0 else 0
        
        wins = [t['pnl'] for t in self.trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in self.trades if t['pnl'] < 0]
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        
        profit_factor = abs(sum(wins) / sum(losses)) if losses and sum(losses) != 0 else 999
        
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        # 最大连续亏损
        max_consecutive_losses = 0
        current_losses = 0
        for t in self.trades:
            if t['pnl'] < 0:
                current_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
            else:
                current_losses = 0
        
        return {
            'symbol': symbol,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(self.total_pnl, 2),
            'total_return': round(total_return, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(self.max_drawdown * 100, 2),
            'max_consecutive_losses': max_consecutive_losses,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.capital, 2),
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }


def format_report(results):
    """格式化报告"""
    if not results:
        return "无结果"
    
    lines = []
    lines.append("=" * 60)
    lines.append("回测报告: " + results['symbol'])
    lines.append("=" * 60)
    
    lines.append("")
    lines.append("[基本信息]")
    lines.append("初始资金: $" + str(results['initial_capital']))
    lines.append("最终资金: $" + str(results['final_capital']))
    lines.append("总收益率: " + str(results['total_return']) + "%")
    lines.append("总盈亏: $" + str(results['total_pnl']))
    
    lines.append("")
    lines.append("[交易统计]")
    lines.append("总交易: " + str(results['total_trades']) + " 笔")
    lines.append("盈利: " + str(results['winning_trades']) + " 笔")
    lines.append("亏损: " + str(results['losing_trades']) + " 笔")
    lines.append("胜率: " + str(results['win_rate']) + "%")
    
    lines.append("")
    lines.append("[盈亏分析]")
    lines.append("平均盈利: $" + str(results['avg_win']))
    lines.append("平均亏损: $" + str(results['avg_loss']))
    lines.append("盈亏比: " + str(results['profit_factor']))
    lines.append("最大回撤: " + str(results['max_drawdown']) + "%")
    lines.append("最大连续亏损: " + str(results['max_consecutive_losses']) + " 次")
    
    # 交易明细
    if results['trades']:
        lines.append("")
        lines.append("[交易明细]")
        lines.append("-" * 60)
        
        for i, t in enumerate(results['trades'][:15], 1):
            pnl_str = "+$" + str(t['pnl']) if t['pnl'] >= 0 else "-$" + str(abs(t['pnl']))
            lines.append(str(i).ljust(4) + t['type'].ljust(6) + 
                        ("$" + str(t['entry_price'])).ljust(12) + 
                        ("$" + str(t['exit_price'])).ljust(12) + 
                        pnl_str.ljust(10) + t['exit_reason'])
    
    lines.append("")
    lines.append("=" * 60)
    
    # 评级
    if results['win_rate'] >= 50 and results['profit_factor'] >= 1.5:
        lines.append("评级: 优秀 (5/5)")
    elif results['win_rate'] >= 40 and results['profit_factor'] >= 1.2:
        lines.append("评级: 良好 (4/5)")
    elif results['win_rate'] >= 35 and results['profit_factor'] >= 1.0:
        lines.append("评级: 一般 (3/5)")
    else:
        lines.append("评级: 较差 (2/5)")
    
    lines.append("=" * 60)
    
    return '\n'.join(lines)


# 运行回测
if __name__ == "__main__":
    print("OKX策略回测系统")
    print("=" * 60)
    
    proxy = "http://127.0.0.1:7890"
    
    symbols = ['TSLA-USDT-SWAP', 'AMZN-USDT-SWAP', 'BTC-USDT-SWAP', 'MSFT-USDT-SWAP']
    
    all_results = []
    
    for symbol in symbols:
        print("\n回测: " + symbol)
        bt = Backtester(initial_capital=10000, risk_per_trade=0.02)
        results = bt.run_backtest(symbol, proxy)
        
        if results:
            print(format_report(results))
            all_results.append(results)
        else:
            print("回测失败")
    
    # 汇总
    if all_results:
        print("\n" + "=" * 60)
        print("汇总统计")
        print("=" * 60)
        
        total_trades = sum(r['total_trades'] for r in all_results)
        total_wins = sum(r['winning_trades'] for r in all_results)
        total_return = sum(r['total_return'] for r in all_results)
        
        print("总交易: " + str(total_trades) + " 笔")
        print("总胜率: " + str(round(total_wins/total_trades*100, 1) if total_trades > 0 else 0) + "%")
        print("平均收益: " + str(round(total_return/len(all_results), 2)) + "%")
