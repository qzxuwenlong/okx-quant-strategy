# -*- coding: utf-8 -*-
"""
信号生成模块
支持多周期分析
大周期定方向，小周期找时机
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
        
        # RSI历史
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
        
        # SMA历史
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
        
        核心逻辑：
        1. 大周期定方向（顺势交易优先）
        2. 小周期找时机（超卖反弹是逆势，要谨慎）
        3. 信号类型：trend（趋势跟随）或 mean_reversion（均值回归）
        """
        if not indicators:
            return 'hold', 0, []
        
        current = indicators['current']
        sma_50 = indicators['sma_50']
        rsi = indicators['rsi']
        vol_ratio = indicators['vol_ratio']
        
        # =============================================
        # 场景1：大盘BULLISH
        # 策略：趋势跟随做多
        # =============================================
        if market_trend == 'bullish':
            # 做多：价格>MA50 + RSI适中
            if current > sma_50 and rsi < 65:
                score = 3
                reasons = ['大盘看多', '趋势向上']
                
                if rsi < 45:
                    score += 1
                    reasons.append('RSI健康')
                
                if vol_ratio > 1.2:
                    score += 1
                    reasons.append('成交量放大')
                
                if score >= 3:
                    return 'buy', score, reasons, 'trend'
        
        # =============================================
        # 场景2：大盘BEARISH
        # 策略：趋势跟随做空（主）/ 超卖反弹做多（辅）
        # =============================================
        elif market_trend == 'bearish':
            
            # 【主策略】趋势跟随做空
            # 条件：价格<MA50 + RSI>35（不在超卖区）
            if current < sma_50 and rsi > 35:
                is_short, short_score, reasons = self.oneil_short.analyze(
                    indicators['prices'],
                    indicators['highs'],
                    indicators['lows'],
                    indicators['volumes'],
                    indicators['rsi_history'],
                    indicators['sma_20_history'],
                    indicators['sma_50_history']
                )
                
                if is_short and short_score >= 3:
                    reasons.append('价格<MA50')
                    return 'short', short_score, reasons, 'trend'
            
            # 【辅助策略】超卖反弹做多（逆势，小仓位）
            # 条件：RSI<25（严重超卖）+ 价格接近支撑
            elif rsi < 25:
                # 计算是否接近支撑位
                recent_low = min(indicators['lows'][-10:])
                support_distance = (current - recent_low) / recent_low
                
                if support_distance < 0.03:  # 距离支撑位<3%
                    score = 4
                    reasons = ['RSI严重超卖', '接近支撑位', '反弹机会']
                    
                    return 'buy', score, reasons, 'mean_reversion'
        
        # =============================================
        # 场景3：大盘NEUTRAL（震荡市）
        # 策略：均值回归为主
        # =============================================
        elif market_trend == 'neutral':
            # 做多（超卖反弹）：RSI<30
            if rsi < 30:
                score = 3
                reasons = ['RSI超卖', '均值回归']
                
                if current > sma_50:
                    score += 2
                    reasons.append('趋势向上')
                
                if score >= 3:
                    return 'buy', score, reasons, 'mean_reversion'
            
            # 做空（超买回落）：RSI>70 + 欧奈尔信号
            elif rsi > 70:
                score = 3
                reasons = ['RSI超买', '均值回归']
                
                if current < sma_50:
                    score += 2
                    reasons.append('趋势向下')
                
                is_short, short_score, oneil_reasons = self.oneil_short.analyze(
                    indicators['prices'],
                    indicators['highs'],
                    indicators['lows'],
                    indicators['volumes'],
                    indicators['rsi_history'],
                    indicators['sma_20_history'],
                    indicators['sma_50_history']
                )
                
                if is_short:
                    score += short_score
                    reasons.extend(oneil_reasons)
                
                if score >= 4:
                    return 'short', score, reasons, 'mean_reversion'
        
        return 'hold', 0, [], 'none'
    
    def get_signal_details(self, indicators, signal, score, reasons, strategy_type='trend'):
        """获取信号详情"""
        if not indicators or signal == 'hold':
            return {'signal': 'hold', 'score': 0, 'reasons': [], 'strategy_type': 'none'}
        
        current = indicators['atr']
        atr = indicators['atr']
        
        # 趋势跟随：宽止损宽止盈
        # 均值回归：窄止损窄止盈
        if strategy_type == 'trend':
            stop_loss = round(current - (atr * 2), 4)
            take_profit = round(current + (atr * 4), 4)
            position_size = 'normal'  # 正常仓位
        else:  # mean_reversion
            stop_loss = round(current - (atr * 1), 4)
            take_profit = round(current + (atr * 2), 4)
            position_size = 'small'  # 小仓位（逆势）
        
        return {
            'signal': signal,
            'score': score,
            'reasons': reasons,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'strategy_type': strategy_type,
            'position_size': position_size
        }
