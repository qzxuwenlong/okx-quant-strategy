# -*- coding: utf-8 -*-
"""
日本股票策略模块
集成日本交易大师的经典策略
"""

import numpy as np
import pandas as pd

class JapanesePatterns:
    """日本蜡烛图形态识别"""
    
    @staticmethod
    def is_doji(open_p, high, low, close, threshold=0.1):
        """十字星：开盘收盘接近，表示犹豫"""
        body = abs(close - open_p)
        total = high - low
        if total == 0:
            return False
        return body / total < threshold
    
    @staticmethod
    def is_hammer(open_p, high, low, close):
        """锤子线：下影线长，上影线短，底部反转信号"""
        body = abs(close - open_p)
        lower_shadow = min(open_p, close) - low
        upper_shadow = high - max(open_p, close)
        
        if body == 0:
            return False
        
        # 下影线是实体的2倍以上，上影线很短
        return lower_shadow > body * 2 and upper_shadow < body * 0.5
    
    @staticmethod
    def is_engulfing_bullish(prev_open, prev_close, curr_open, curr_close):
        """看涨吞没：前阴后阳，阳包阴"""
        prev_bearish = prev_close < prev_open
        curr_bullish = curr_close > curr_open
        
        if not prev_bearish or not curr_bullish:
            return False
        
        # 当前阳线完全包裹前一根阴线
        return curr_open < prev_close and curr_close > prev_open
    
    @staticmethod
    def is_engulfing_bearish(prev_open, prev_close, curr_open, curr_close):
        """看跌吞没：前阳后阴，阴包阳"""
        prev_bullish = prev_close > prev_open
        curr_bearish = curr_close < curr_open
        
        if not prev_bullish or not curr_bearish:
            return False
        
        return curr_open > prev_close and curr_close < prev_open
    
    @staticmethod
    def is_morning_star(candles):
        """晨星：三根K线组合，底部反转"""
        if len(candles) < 3:
            return False
        
        first = candles[-3]
        second = candles[-2]
        third = candles[-1]
        
        # 第一根大阴线
        first_bearish = first['close'] < first['open'] and (first['open'] - first['close']) / first['open'] > 0.02
        
        # 第二根小实体（十字星最佳）
        second_small = abs(second['close'] - second['open']) < (first['open'] - first['close']) * 0.3
        
        # 第三根大阳线
        third_bullish = third['close'] > third['open'] and (third['close'] - third['open']) / third['open'] > 0.02
        
        # 第三根收盘价高于第一根实体一半
        third_above = third['close'] > (first['open'] + first['close']) / 2
        
        return first_bearish and second_small and third_bullish and third_above
    
    @staticmethod
    def is_evening_star(candles):
        """暮星：三根K线组合，顶部反转"""
        if len(candles) < 3:
            return False
        
        first = candles[-3]
        second = candles[-2]
        third = candles[-1]
        
        # 第一根大阳线
        first_bullish = first['close'] > first['open'] and (first['close'] - first['open']) / first['open'] > 0.02
        
        # 第二根小实体
        second_small = abs(second['close'] - second['open']) < (first['close'] - first['open']) * 0.3
        
        # 第三根大阴线
        third_bearish = third['close'] < third['open'] and (third['open'] - third['close']) / third['open'] > 0.02
        
        # 第三根收盘价低于第一根实体一半
        third_below = third['close'] < (first['open'] + first['close']) / 2
        
        return first_bullish and second_small and third_bearish and third_below


class SakeDenFiveLaws:
    """酒田五法 - 日本经典技术分析"""
    
    @staticmethod
    def three_soldiers(candles):
        """三连阳（三白兵）：强势上涨信号"""
        if len(candles) < 3:
            return False
        
        for i in range(-3, 0):
            if candles[i]['close'] <= candles[i]['open']:
                return False
            # 每根收盘价高于前一根
            if i > -3 and candles[i]['close'] <= candles[i-1]['close']:
                return False
        
        return True
    
    @staticmethod
    def three_crows(candles):
        """三连鸦（三只乌鸦）：强势下跌信号"""
        if len(candles) < 3:
            return False
        
        for i in range(-3, 0):
            if candles[i]['close'] >= candles[i]['open']:
                return False
            # 每根收盘价低于前一根
            if i > -3 and candles[i]['close'] >= candles[i-1]['close']:
                return False
        
        return True
    
    @staticmethod
    def three_mountain(candles, lookback=20):
        """三尊天井（头肩顶）：重要顶部形态"""
        if len(candles) < lookback:
            return False
        
        highs = [c['high'] for c in candles[-lookback:]]
        
        # 找三个高点
        peaks = []
        for i in range(1, len(highs)-1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
        
        if len(peaks) < 3:
            return False
        
        # 中间高点最高
        last_three = peaks[-3:]
        return last_three[1][1] > last_three[0][1] and last_three[1][1] > last_three[2][1]
    
    @staticmethod
    def three_river(candles, lookback=20):
        """三川（头肩底）：重要底部形态"""
        if len(candles) < lookback:
            return False
        
        lows = [c['low'] for c in candles[-lookback:]]
        
        # 找三个低点
        troughs = []
        for i in range(1, len(lows)-1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append((i, lows[i]))
        
        if len(troughs) < 3:
            return False
        
        # 中间低点最低
        last_three = troughs[-3:]
        return last_three[1][1] < last_three[0][1] and last_three[1][1] < last_three[2][1]


class CIStrategy:
    """cis风格策略 - 日内动量突破"""
    
    def __init__(self):
        self.name = "CIS日内动量"
    
    def generate_signal(self, df):
        """
        cis风格信号：
        - 突破前日高点做多
        - 跌破前日低点做空
        - 快速止损，让利润奔跑
        """
        if len(df) < 20:
            return 'hold', 0, []
        
        current = df['close'].iloc[-1]
        prev_high = df['high'].iloc[-2]
        prev_low = df['low'].iloc[-2]
        
        # 成交量确认
        vol_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        
        # 突破做多
        if current > prev_high and vol_ratio > 1.5:
            return 'buy', 4, ['突破前日高点', '成交量放大']
        
        # 跌破做空
        elif current < prev_low and vol_ratio > 1.5:
            return 'short', 4, ['跌破前日低点', '成交量放大']
        
        return 'hold', 0, []


class BNFStrategy:
    """BNF风格策略 - 大波段趋势跟随"""
    
    def __init__(self):
        self.name = "BNF大波段"
    
    def generate_signal(self, df):
        """
        BNF风格信号：
        - 长期趋势跟随
        - 大周期均线判断方向
        - 回调入场，持有到趋势结束
        """
        if len(df) < 200:
            return 'hold', 0, []
        
        current = df['close'].iloc[-1]
        ma_200 = df['close'].rolling(200).mean().iloc[-1]
        ma_50 = df['close'].rolling(50).mean().iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # 上升趋势中回调买入
        if current > ma_200 and ma_50 > ma_200:
            if rsi < 40:  # 回调
                return 'buy', 5, ['长期上升趋势', '回调买入机会']
        
        # 下降趋势中反弹做空
        elif current < ma_200 and ma_50 < ma_200:
            if rsi > 60:  # 反弹
                return 'short', 5, ['长期下降趋势', '反弹做空机会']
        
        return 'hold', 0, []


class JapaneseStrategyFactory:
    """日本策略工厂"""
    
    @staticmethod
    def create_strategy(strategy_type='candlestick'):
        strategies = {
            'candlestick': JapanesePatterns,
            'sake_den': SakeDenFiveLaws,
            'cis': CIStrategy,
            'bnf': BNFStrategy
        }
        
        if strategy_type not in strategies:
            raise ValueError(f"未知策略: {strategy_type}")
        
        return strategies[strategy_type]
    
    @staticmethod
    def list_strategies():
        return ['candlestick', 'sake_den', 'cis', 'bnf']
