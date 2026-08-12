# -*- coding: utf-8 -*-
"""完整回测测试（支持新策略）"""

import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from src.strategies.backtester import Backtester, format_report
from src.core.signal_generator import SignalGenerator

class NewBacktester(Backtester):
    """支持新策略的回测器"""
    
    def __init__(self, initial_capital=10000, risk_per_trade=0.02, max_positions=5):
        super().__init__(initial_capital, risk_per_trade, max_positions)
        self.signal_generator = SignalGenerator()
    
    def row_to_indicators(self, row, df, idx):
        """将DataFrame行转换为indicators字典"""
        # 获取历史数据用于计算
        prices = df['close'].iloc[max(0, idx-50):idx+1].tolist()
        volumes = df['vol'].iloc[max(0, idx-50):idx+1].tolist()
        
        return {
            'current': row['close'],
            'prices': prices,
            'highs': df['high'].iloc[max(0, idx-50):idx+1].tolist(),
            'lows': df['low'].iloc[max(0, idx-50):idx+1].tolist(),
            'volumes': volumes,
            'sma_20': row['sma_20'] if not pd.isna(row['sma_20']) else 0,
            'sma_50': row['sma_50'] if not pd.isna(row['sma_50']) else 0,
            'rsi': row['rsi'] if not pd.isna(row['rsi']) else 50,
            'rsi_history': [],
            'sma_20_history': [],
            'sma_50_history': [],
            'vol_ratio': row['vol_ratio'] if not pd.isna(row['vol_ratio']) else 1,
            'atr': row['atr'] if not pd.isna(row['atr']) else 0
        }
    
    def get_market_trend(self, df, idx):
        """判断大盘趋势"""
        if idx < 50:
            return 'neutral'
        
        sma_50 = df['sma_50'].iloc[idx]
        rsi = df['rsi'].iloc[idx]
        current = df['close'].iloc[idx]
        
        if pd.isna(sma_50) or pd.isna(rsi):
            return 'neutral'
        
        if current > sma_50 and rsi > 45:
            return 'bullish'
        elif current < sma_50 and rsi < 55:
            return 'bearish'
        
        return 'neutral'
    
    def run_backtest_new(self, symbol, proxy=None):
        """运行回测（新策略）"""
        print("=" * 60)
        print("回测: " + symbol + " (新策略)")
        print("=" * 60)
        
        # 获取数据
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
            
            # 判断大盘趋势
            market_trend = self.get_market_trend(df, i)
            
            # 转换为indicators格式
            indicators = self.row_to_indicators(row, df, i)
            
            # 更新持仓盈亏
            self.update_positions(row)
            
            # 检查出场
            self.check_exits(row)
            
            # 生成信号（使用新策略）
            result = self.signal_generator.generate_signal(indicators, market_trend)
            signal = result[0]
            score = result[1]
            
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

# 运行回测
print("=" * 60)
print("新策略回测测试")
print("=" * 60)

# 测试SPY
bt = NewBacktester(initial_capital=10000)
results = bt.run_backtest_new('SPY-USDT-SWAP')

if results:
    print(format_report(results))
