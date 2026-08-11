# -*- coding: utf-8 -*-
"""
信号生成模块
整合欧奈尔卖空理论
"""

import numpy as np
from src.core.oneil_short import OneilShortSignal

class SignalGenerator:
    def __init__(self):
        self.oneil_short = OneilShortSignal()
    
    def calculate_indicators(self, prices, volumes):
        """计算技术指标"""
        if len(prices) < 50:
            return None
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        # 计算RSI
        deltas = np.diff(prices[-15:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # 成交量
        vol_sma = np.mean(volumes[-20:])
        vol_ratio = volumes[-1] / vol_sma if vol_sma > 0 else 0
        
        # ATR
        highs = [max(prices[i], prices[i-1]) for i in range(1, len(prices))]
        lows = [min(prices[i], prices[i-1]) for i in range(1, len(prices))]
        trs = [h - l for h, l in zip(highs[-14:], lows[-14:])]
        atr = np.mean(trs)
        
        # RSI历史（用于欧奈尔卖空判断）
        rsi_history = []
        for i in range(max(0, len(prices)-20), len(prices)):
            if i >= 14:
                d = np.diff(prices[i-14:i+1])
                g = np.where(d > 0, d, 0)
                l = np.where(d < 0, -d, 0)
                ag = np.mean(g)
                al = np.mean(l)
                r = ag / al if al > 0 else 100
                rsi_history.append(100 - (100 / (1 + r)))
        
        # SMA历史（用于均线死叉判断）
        sma_20_history = []
        sma_50_history = []
        for i in range(max(0, len(prices)-5), len(prices)):
            if i >= 20:
                sma_20_history.append(np.mean(prices[i-20:i]))
            if i >= 50:
                sma_50_history.append(np.mean(prices[i-50:i]))
        
        return {
            'current': prices[-1],
            'prices': prices,
            'highs': highs,
            'lows': lows,
            'volumes': volumes,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'rsi_history': rsi_history,
            'sma_20_history': sma_20_history,
            'sma_50_history': sma_50_history,
            'vol_ratio': vol_ratio,
            'atr': atr
        }
    
    def get_market_trend(self, sp500_indicators):
        """判断大盘趋势"""
        if not sp500_indicators:
            return 'neutral'
        
        current = sp500_indicators['current']
        sma_50 = sp500_indicators['sma_50']
        rsi = sp500_indicators['rsi']
        
        if current > sma_50 and rsi > 45:
            return 'bullish'
        elif current < sma_50 and rsi < 55:
            return 'bearish'
        
        return 'neutral'
    
    def generate_signal(self, indicators, market_trend='neutral'):
        """
        生成交易信号
        
        做多：趋势向上 + RSI适中 + 成交量放大
        做空：欧奈尔卖空信号 + 大盘看空
        """
        if not indicators:
            return 'hold', 0, []
        
        current = indicators['current']
        sma_50 = indicators['sma_50']
        rsi = indicators['rsi']
        vol_ratio = indicators['vol_ratio']
        
        # ============== 做多信号 ==============
        # 大盘看多或中性时才做多
        if market_trend in ['bullish', 'neutral']:
            long_score = 0
            
            if current > sma_50:
                long_score += 3
            
            if rsi < 30:
                long_score += 2
            elif rsi < 45:
                long_score += 2
            elif rsi < 60:
                long_score += 1
            
            if vol_ratio > 1.2:
                long_score += 1
            
            if long_score >= 5 and 25 < rsi < 65:
                return 'buy', long_score, ['趋势向上', 'RSI适中']
            elif long_score >= 4 and rsi < 60:
                return 'buy', long_score, ['趋势向上']
        
        # ============== 做空信号（欧奈尔） ==============
        # 大盘看空或中性时才做空
        if market_trend in ['bearish', 'neutral']:
            # 使用欧奈尔卖空信号
            is_short, short_score, reasons = self.oneil_short.analyze(
                indicators['prices'],
                indicators['highs'],
                indicators['lows'],
                indicators['volumes'],
                indicators['rsi_history'],
                indicators['sma_20_history'],
                indicators['sma_50_history']
            )
            
            # 额外条件：价格在均线下方
            if current < sma_50:
                short_score += 2
                reasons.append('价格<MA50')
            
            # RSI偏高
            if rsi > 55:
                short_score += 1
                reasons.append('RSI偏高')
            
            if is_short and short_score >= 4:
                return 'short', short_score, reasons
        
        return 'hold', 0, []
    
    def get_signal_details(self, indicators, signal, score, reasons):
        """获取信号详情"""
        if not indicators or signal == 'hold':
            return {'signal': 'hold', 'score': 0, 'reasons': []}
        
        current = indicators['current']
        atr = indicators['atr']
        
        if signal == 'buy':
            stop_loss = round(current - (atr * 2), 4)
            take_profit = round(current + (atr * 4), 4)
        else:
            stop_loss = round(current + (atr * 2), 4)
            take_profit = round(current - (atr * 4), 4)
        
        return {
            'signal': signal,
            'score': score,
            'reasons': reasons,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
