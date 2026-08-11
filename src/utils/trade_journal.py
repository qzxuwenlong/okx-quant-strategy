# -*- coding: utf-8 -*-
"""
交易日志模块
记录、统计、复盘
"""

import json
import os
from datetime import datetime

class TradeJournal:
    """交易日志"""
    
    def __init__(self, log_file='trade_log.json'):
        self.log_file = log_file
        self.trades = []
        self.load_trades()
    
    def load_trades(self):
        """加载历史交易"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.trades = json.load(f)
            except:
                self.trades = []
    
    def save_trades(self):
        """保存交易记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)
    
    def open_trade(self, symbol, trade_type, entry_price, size, 
                   stop_loss=None, take_profit=None, 
                   signal='', score=0, reasons=None, notes=''):
        """
        记录开仓
        
        Args:
            symbol: 交易对
            trade_type: 'long' 或 'short'
            entry_price: 入场价
            size: 仓位大小
            stop_loss: 止损价
            take_profit: 止盈价
            signal: 信号类型
            score: 信号得分
            reasons: 入场理由列表
            notes: 备注
        """
        trade = {
            'id': len(self.trades) + 1,
            'symbol': symbol,
            'type': trade_type,
            'status': 'open',
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'entry_price': entry_price,
            'size': size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signal': signal,
            'score': score,
            'entry_reasons': reasons or [],
            'notes': notes,
            'exit_time': None,
            'exit_price': None,
            'exit_reason': None,
            'pnl': None,
            'pnl_pct': None,
            'hold_duration': None,
            'max_drawdown': None,
            'max_profit': None
        }
        
        self.trades.append(trade)
        self.save_trades()
        
        return trade['id']
    
    def close_trade(self, trade_id, exit_price, exit_reason='', notes=''):
        """
        记录平仓
        
        Args:
            trade_id: 交易ID
            exit_price: 出场价
            exit_reason: 出场原因
            notes: 备注
        """
        for trade in self.trades:
            if trade['id'] == trade_id and trade['status'] == 'open':
                trade['status'] = 'closed'
                trade['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                trade['exit_price'] = exit_price
                trade['exit_reason'] = exit_reason
                trade['notes'] = trade.get('notes', '') + ' | ' + notes
                
                # 计算盈亏
                entry = trade['entry_price']
                size = trade['size']
                
                if trade['type'] == 'long':
                    pnl = (exit_price - entry) * size
                else:
                    pnl = (entry - exit_price) * size
                
                trade['pnl'] = round(pnl, 2)
                trade['pnl_pct'] = round(pnl / (entry * size) * 100, 2)
                
                # 计算持仓时长
                entry_time = datetime.strptime(trade['entry_time'], '%Y-%m-%d %H:%M:%S')
                exit_time = datetime.strptime(trade['exit_time'], '%Y-%m-%d %H:%M:%S')
                duration = exit_time - entry_time
                trade['hold_duration'] = str(duration)
                
                self.save_trades()
                return trade
        
        return None
    
    def update_trade(self, trade_id, current_price):
        """更新持仓盈亏"""
        for trade in self.trades:
            if trade['id'] == trade_id and trade['status'] == 'open':
                entry = trade['entry_price']
                size = trade['size']
                
                if trade['type'] == 'long':
                    pnl = (current_price - entry) * size
                else:
                    pnl = (entry - current_price) * size
                
                pnl_pct = pnl / (entry * size) * 100
                
                # 更新最大回撤和最大盈利
                if trade.get('max_drawdown') is None or pnl_pct < trade['max_drawdown']:
                    trade['max_drawdown'] = round(pnl_pct, 2)
                if trade.get('max_profit') is None or pnl_pct > trade['max_profit']:
                    trade['max_profit'] = round(pnl_pct, 2)
                
                return {'pnl': round(pnl, 2), 'pnl_pct': round(pnl_pct, 2)}
        
        return None
    
    def get_open_trades(self):
        """获取所有持仓"""
        return [t for t in self.trades if t['status'] == 'open']
    
    def get_closed_trades(self):
        """获取所有已平仓"""
        return [t for t in self.trades if t['status'] == 'closed']
    
    def get_statistics(self):
        """获取统计数据"""
        closed = self.get_closed_trades()
        
        if not closed:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_win': 0,
                'max_loss': 0,
                'avg_hold_duration': 'N/A'
            }
        
        total = len(closed)
        wins = [t for t in closed if t['pnl'] > 0]
        losses = [t for t in closed if t['pnl'] <= 0]
        
        total_pnl = sum(t['pnl'] for t in closed)
        avg_pnl = total_pnl / total if total > 0 else 0
        
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        
        profit_factor = abs(sum(t['pnl'] for t in wins) / sum(t['pnl'] for t in losses)) if losses and sum(t['pnl'] for t in losses) != 0 else 999
        
        max_win = max(t['pnl'] for t in closed) if closed else 0
        max_loss = min(t['pnl'] for t in closed) if closed else 0
        
        # 平均持仓时长
        durations = []
        for t in closed:
            if t.get('hold_duration'):
                try:
                    parts = t['hold_duration'].split(', ')
                    if len(parts) == 2:
                        days = int(parts[0].split(' ')[0])
                        time_parts = parts[1].split(':')
                        hours = int(time_parts[0])
                        durations.append(days * 24 + hours)
                    else:
                        time_parts = parts[0].split(':')
                        hours = int(time_parts[0])
                        durations.append(hours)
                except:
                    pass
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_trades': total,
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': round(len(wins) / total * 100, 2) if total > 0 else 0,
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(avg_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_win': round(max_win, 2),
            'max_loss': round(max_loss, 2),
            'avg_hold_hours': round(avg_duration, 1)
        }
    
    def format_trade(self, trade):
        """格式化单笔交易"""
        lines = []
        lines.append("-" * 50)
        lines.append("Trade #" + str(trade['id']) + " | " + trade['symbol'] + " | " + trade['type'].upper())
        lines.append("Status: " + trade['status'].upper())
        
        if trade['status'] == 'open':
            lines.append("Entry: $" + str(trade['entry_price']) + " @ " + trade['entry_time'])
            lines.append("Size: " + str(trade['size']))
            if trade.get('stop_loss'):
                lines.append("Stop Loss: $" + str(trade['stop_loss']))
            if trade.get('take_profit'):
                lines.append("Take Profit: $" + str(trade['take_profit']))
            if trade.get('signal'):
                lines.append("Signal: " + trade['signal'] + " (Score: " + str(trade.get('score', 0)) + ")")
            if trade.get('entry_reasons'):
                lines.append("Reasons: " + ', '.join(trade['entry_reasons']))
        else:
            lines.append("Entry: $" + str(trade['entry_price']) + " @ " + trade['entry_time'])
            lines.append("Exit: $" + str(trade['exit_price']) + " @ " + trade['exit_time'])
            lines.append("Duration: " + str(trade.get('hold_duration', 'N/A')))
            lines.append("PnL: $" + str(trade['pnl']) + " (" + str(trade['pnl_pct']) + "%)")
            lines.append("Exit Reason: " + trade.get('exit_reason', 'N/A'))
            if trade.get('max_drawdown'):
                lines.append("Max Drawdown: " + str(trade['max_drawdown']) + "%")
            if trade.get('max_profit'):
                lines.append("Max Profit: " + str(trade['max_profit']) + "%")
        
        if trade.get('notes'):
            lines.append("Notes: " + trade['notes'])
        
        return '\n'.join(lines)
    
    def format_statistics(self, stats):
        """格式化统计数据"""
        lines = []
        lines.append("=" * 50)
        lines.append("Trading Statistics")
        lines.append("=" * 50)
        lines.append("")
        lines.append("[Overview]")
        lines.append("  Total Trades: " + str(stats['total_trades']))
        lines.append("  Winning: " + str(stats['winning_trades']))
        lines.append("  Losing: " + str(stats['losing_trades']))
        lines.append("  Win Rate: " + str(stats['win_rate']) + "%")
        lines.append("")
        lines.append("[PnL]")
        lines.append("  Total PnL: $" + str(stats['total_pnl']))
        lines.append("  Average PnL: $" + str(stats['avg_pnl']))
        lines.append("  Average Win: $" + str(stats['avg_win']))
        lines.append("  Average Loss: $" + str(stats['avg_loss']))
        lines.append("  Profit Factor: " + str(stats['profit_factor']))
        lines.append("  Max Win: $" + str(stats['max_win']))
        lines.append("  Max Loss: $" + str(stats['max_loss']))
        lines.append("")
        lines.append("[Duration]")
        lines.append("  Avg Hold Time: " + str(stats['avg_hold_hours']) + " hours")
        lines.append("")
        lines.append("=" * 50)
        
        # 评级
        if stats['win_rate'] >= 60 and stats['profit_factor'] >= 2:
            lines.append("Rating: Excellent (5/5)")
        elif stats['win_rate'] >= 50 and stats['profit_factor'] >= 1.5:
            lines.append("Rating: Good (4/5)")
        elif stats['win_rate'] >= 40 and stats['profit_factor'] >= 1:
            lines.append("Rating: Average (3/5)")
        else:
            lines.append("Rating: Poor (2/5)")
        
        lines.append("=" * 50)
        
        return '\n'.join(lines)
    
    def format_all_trades(self, limit=20):
        """格式化所有交易"""
        lines = []
        lines.append("=" * 50)
        lines.append("Trade Journal")
        lines.append("=" * 50)
        
        # 持仓中的交易
        open_trades = self.get_open_trades()
        if open_trades:
            lines.append("")
            lines.append("[Open Positions]")
            for trade in open_trades[-limit:]:
                lines.append(self.format_trade(trade))
        
        # 已平仓交易
        closed_trades = self.get_closed_trades()
        if closed_trades:
            lines.append("")
            lines.append("[Closed Trades] (Last " + str(limit) + ")")
            for trade in closed_trades[-limit:]:
                lines.append(self.format_trade(trade))
        
        return '\n'.join(lines)
    
    def export_csv(self, filename='trades.csv'):
        """导出为CSV"""
        import csv
        
        if not self.trades:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Symbol', 'Type', 'Status', 'Entry Time', 'Entry Price', 
                           'Exit Time', 'Exit Price', 'Size', 'PnL', 'PnL %', 
                           'Hold Duration', 'Exit Reason', 'Signal', 'Score'])
            
            for t in self.trades:
                writer.writerow([
                    t['id'], t['symbol'], t['type'], t['status'],
                    t['entry_time'], t['entry_price'],
                    t.get('exit_time', ''), t.get('exit_price', ''),
                    t['size'], t.get('pnl', ''), t.get('pnl_pct', ''),
                    t.get('hold_duration', ''), t.get('exit_reason', ''),
                    t.get('signal', ''), t.get('score', '')
                ])
        
        print("Exported to " + filename)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("Trade Journal System")
    print("=" * 60)
    
    journal = TradeJournal('test_journal.json')
    
    # 模拟开仓
    print("\n1. Opening trade...")
    trade_id = journal.open_trade(
        symbol='TSLA-USDT-SWAP',
        trade_type='long',
        entry_price=331.50,
        size=10,
        stop_loss=328.00,
        take_profit=340.00,
        signal='strong_buy',
        score=7,
        reasons=['趋势向上', 'RSI适中', '成交量放大'],
        notes='测试交易'
    )
    print("Trade opened: ID=" + str(trade_id))
    
    # 模拟平仓
    print("\n2. Closing trade...")
    journal.close_trade(trade_id, 335.50, '止盈', '测试平仓')
    print("Trade closed")
    
    # 显示统计
    print("\n3. Statistics:")
    stats = journal.get_statistics()
    print(journal.format_statistics(stats))
    
    # 显示所有交易
    print("\n4. All Trades:")
    print(journal.format_all_trades())
