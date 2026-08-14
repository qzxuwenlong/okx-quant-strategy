# -*- coding: utf-8 -*-
"""
综合信号生成器
集成：欧奈尔 + 威科夫 + 日本蜡烛图 + cis/BNF策略
"""

import numpy as np
import sys
sys.path.insert(0, '.')

from src.core.japanese_strategy import JapanesePatterns, SakeDenFiveLaws, CIStrategy, BNFStrategy

class ComprehensiveSignalGenerator:
    """综合信号生成器"""
    
    def __init__(self):
        self.japanese_patterns = JapanesePatterns()
        self.sake_den = SakeDenFiveLaws()
        self.cis_strategy = CIStrategy()
        self.bnf_strategy = BNFStrategy()
    
    def calculate_indicators(self, prices, volumes, opens=None, highs=None, lows=None):
        """计算技术指标"""
        if len(prices) < 50:
            return None
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        # RSI
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
        if highs and lows:
            trs = []
            for i in range(1, len(prices)):
                tr = max(highs[i] - lows[i], 
                        abs(highs[i] - prices[i-1]), 
                        abs(lows[i] - prices[i-1]))
                trs.append(tr)
            atr = np.mean(trs[-14:])
        else:
            atr = 0
        
        # 蜡烛图数据
        candles = None
        if opens and highs and lows:
            candles = []
            for i in range(len(prices)):
                candles.append({
                    'open': opens[i],
                    'high': highs[i],
                    'low': lows[i],
                    'close': prices[i],
                    'volume': volumes[i]
                })
        
        return {
            'current': prices[-1],
            'prices': prices,
            'volumes': volumes,
            'candles': candles,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'vol_ratio': vol_ratio,
            'atr': atr
        }
    
    def generate_comprehensive_signal(self, indicators, market_trend='neutral'):
        """
        综合信号生成
        整合多种策略的信号
        """
        if not indicators:
            return 'hold', 0, [], 'none', 'none'
        
        signals = []
        
        # 1. 基础趋势信号
        trend_signal, trend_score, trend_reasons = self._trend_signal(indicators, market_trend)
        if trend_signal != 'hold':
            signals.append(('trend', trend_signal, trend_score, trend_reasons))
        
        # 2. 日本蜡烛图信号
        candle_signal, candle_score, candle_reasons = self._candlestick_signal(indicators)
        if candle_signal != 'hold':
            signals.append(('candlestick', candle_signal, candle_score, candle_reasons))
        
        # 3. cis日内动量信号
        if indicators.get('candles') and len(indicators['candles']) >= 20:
            cis_df = self._candles_to_df(indicators['candles'])
            cis_signal, cis_score, cis_reasons = self.cis_strategy.generate_signal(cis_df)
            if cis_signal != 'hold':
                signals.append(('cis', cis_signal, cis_score, cis_reasons))
        
        # 4. BNF大波段信号
        if indicators.get('candles') and len(indicators['candles']) >= 200:
            bnf_df = self._candles_to_df(indicators['candles'])
            bnf_signal, bnf_score, bnf_reasons = self.bnf_strategy.generate_signal(bnf_df)
            if bnf_signal != 'hold':
                signals.append(('bnf', bnf_signal, bnf_score, bnf_reasons))
        
        # 综合判断
        if not signals:
            return 'hold', 0, [], 'none', 'none'
        
        # 统计做多和做空信号
        buy_signals = [s for s in signals if s[1] == 'buy']
        short_signals = [s for s in signals if s[1] == 'short']
        
        # 多信号共振
        if len(buy_signals) >= 2:
            # 多个策略同时看多
            total_score = sum(s[2] for s in buy_signals)
            all_reasons = []
            for s in buy_signals:
                all_reasons.extend(s[3])
            strategy_names = [s[0] for s in buy_signals]
            return 'buy', min(total_score, 10), all_reasons[:3], 'multi_confirm', '+'.join(strategy_names)
        
        elif len(short_signals) >= 2:
            # 多个策略同时看空
            total_score = sum(s[2] for s in short_signals)
            all_reasons = []
            for s in short_signals:
                all_reasons.extend(s[3])
            strategy_names = [s[0] for s in short_signals]
            return 'short', min(total_score, 10), all_reasons[:3], 'multi_confirm', '+'.join(strategy_names)
        
        elif buy_signals:
            # 只有做多信号
            best = max(buy_signals, key=lambda x: x[2])
            return best[1], best[2], best[3], 'single', best[0]
        
        elif short_signals:
            # 只有做空信号
            best = max(short_signals, key=lambda x: x[2])
            return best[1], best[2], best[3], 'single', best[0]
        
        return 'hold', 0, [], 'none', 'none'
    
    def _trend_signal(self, indicators, market_trend):
        """基础趋势信号"""
        current = indicators['current']
        sma_50 = indicators['sma_50']
        rsi = indicators['rsi']
        vol_ratio = indicators['vol_ratio']
        
        if market_trend == 'bullish':
            if current > sma_50 and rsi < 65:
                score = 3
                reasons = ['趋势向上']
                if rsi < 45:
                    score += 1
                    reasons.append('RSI健康')
                if vol_ratio > 1.2:
                    score += 1
                    reasons.append('成交量放大')
                return 'buy', score, reasons
        
        elif market_trend == 'bearish':
            if current < sma_50 and rsi > 35:
                return 'short', 3, ['趋势向下']
        
        else:
            if rsi < 30:
                return 'buy', 3, ['超卖反弹']
            elif rsi > 70:
                return 'short', 3, ['超买回落']
        
        return 'hold', 0, []
    
    def _candlestick_signal(self, indicators):
        """日本蜡烛图信号"""
        candles = indicators.get('candles')
        if not candles or len(candles) < 3:
            return 'hold', 0, []
        
        # 检查各种形态
        patterns = []
        
        # 锤子线（底部反转）
        if self.japanese_patterns.is_hammer(
            candles[-1]['open'], candles[-1]['high'], 
            candles[-1]['low'], candles[-1]['close']
        ):
            patterns.append(('buy', 3, ['锤子线']))
        
        # 看涨吞没
        if self.japanese_patterns.is_engulfing_bullish(
            candles[-2]['open'], candles[-2]['close'],
            candles[-1]['open'], candles[-1]['close']
        ):
            patterns.append(('buy', 4, ['看涨吞没']))
        
        # 看跌吞没
        if self.japanese_patterns.is_engulfing_bearish(
            candles[-2]['open'], candles[-2]['close'],
            candles[-1]['open'], candles[-1]['close']
        ):
            patterns.append(('short', 4, ['看跌吞没']))
        
        # 晨星（底部反转）
        if self.japanese_patterns.is_morning_star(candles[-3:]):
            patterns.append(('buy', 5, ['晨星形态']))
        
        # 暮星（顶部反转）
        if self.japanese_patterns.is_evening_star(candles[-3:]):
            patterns.append(('short', 5, ['暮星形态']))
        
        # 三白兵（强势上涨）
        if self.sake_den.three_soldiers(candles[-3:]):
            patterns.append(('buy', 5, ['三白兵']))
        
        # 三连鸦（强势下跌）
        if self.sake_den.three_crows(candles[-3:]):
            patterns.append(('short', 5, ['三连鸦']))
        
        if patterns:
            # 返回最强信号
            best = max(patterns, key=lambda x: x[1])
            return best
        
        return 'hold', 0, []
    
    def _candles_to_df(self, candles):
        """将蜡烛图数据转换为DataFrame"""
        import pandas as pd
        df = pd.DataFrame(candles)
        return df
