# -*- coding: utf-8 -*-
"""
欧奈尔卖空信号判断
来源：《How to Make Money Selling Stocks Short》
"""

import numpy as np

class OneilShortSignal:
    """欧奈尔卖空信号"""
    
    def check_top_patterns(self, prices, highs, lows):
        """
        检查顶部形态
        
        返回: (是否出现顶部, 形态名称)
        """
        if len(prices) < 20:
            return False, ''
        
        # ============ 1. 双重顶 ============
        # 两次测试同一高点后下跌
        recent_high = max(highs[-20:])
        second_test = max(highs[-10:])
        
        if abs(recent_high - second_test) / recent_high < 0.02:  # 两次高点接近
            if prices[-1] < prices[-10]:  # 价格下跌
                return True, '双重顶'
        
        # ============ 2. 头肩顶 ============
        # 左肩 < 头 > 右肩，右肩低于头
        if len(highs) >= 30:
            left_shoulder = max(highs[-30:-20])
            head = max(highs[-20:-10])
            right_shoulder = max(highs[-10:])
            
            if head > left_shoulder and head > right_shoulder:
                if right_shoulder < head * 0.98:  # 右肩明显低于头
                    return True, '头肩顶'
        
        # ============ 3. 圆弧顶 ============
        # 价格缓慢上涨后缓慢下跌
        if len(prices) >= 20:
            mid = len(prices) - 10
            left_rise = (prices[mid] - prices[mid-10]) / prices[mid-10]
            right_fall = (prices[mid] - prices[-1]) / prices[mid]
            
            if left_rise > 0.05 and right_fall > 0.03:
                return True, '圆弧顶'
        
        return False, ''
    
    def check_breakout_failure(self, prices, highs):
        """
        检查突破失败
        
        突破后迅速回落 = 卖空信号
        """
        if len(prices) < 10:
            return False
        
        # 近期高点
        recent_high = max(highs[-10:-2])
        
        # 价格曾突破高点
        if highs[-2] > recent_high:
            # 但迅速回落
            if prices[-1] < highs[-2] * 0.97:  # 回落3%以上
                return True
        
        return False
    
    def check_volume_divergence(self, prices, volumes):
        """
        检查量价背离
        
        价格创新高但成交量萎缩 = 卖空信号
        """
        if len(prices) < 20 or len(volumes) < 20:
            return False
        
        # 价格创新高
        price_new_high = prices[-1] >= max(prices[-20:])
        
        # 成交量萎缩
        vol_avg = np.mean(volumes[-20:])
        vol_recent = np.mean(volumes[-5:])
        volume_declining = vol_recent < vol_avg * 0.8
        
        if price_new_high and volume_declining:
            return True
        
        return False
    
    def check_leadership_breakdown(self, rsi_history):
        """
        检查领导股转弱
        
        RSI从高位快速下跌 = 卖空信号
        """
        if len(rsi_history) < 10:
            return False
        
        # RSI曾超过70（超买）
        was_overbought = max(rsi_history[-10:]) > 70
        
        # 现在RSI快速下跌
        rsi_dropping = rsi_history[-1] < rsi_history[-3] - 10
        
        if was_overbought and rsi_dropping:
            return True
        
        return False
    
    def check_moving_average_cross(self, sma_short, sma_long):
        """
        检查均线死叉
        
        短期均线下穿长期均线 = 卖空信号
        """
        if len(sma_short) < 3 or len(sma_long) < 3:
            return False
        
        # 短期均线下穿长期均线
        if sma_short[-1] < sma_long[-1] and sma_short[-2] >= sma_long[-2]:
            return True
        
        return False
    
    def analyze(self, prices, highs, lows, volumes, rsi_history, sma_20, sma_50):
        """
        综合分析卖空信号
        
        返回: (是否卖空, 得分, 原因列表)
        """
        score = 0
        reasons = []
        
        # 1. 顶部形态
        is_top, pattern = self.check_top_patterns(prices, highs, lows)
        if is_top:
            score += 3
            reasons.append(pattern)
        
        # 2. 突破失败
        if self.check_breakout_failure(prices, highs):
            score += 2
            reasons.append('突破失败')
        
        # 3. 量价背离
        if self.check_volume_divergence(prices, volumes):
            score += 2
            reasons.append('量价背离')
        
        # 4. 领导股转弱
        if self.check_leadership_breakdown(rsi_history):
            score += 2
            reasons.append('RSI高位反转')
        
        # 5. 均线死叉
        if self.check_moving_average_cross(sma_20, sma_50):
            score += 2
            reasons.append('均线死叉')
        
        # 判断是否卖空
        is_short = score >= 4  # 至少满足2个条件
        
        return is_short, score, reasons


# 测试
if __name__ == '__main__':
    print('欧奈尔卖空信号模块')
    print('')
    print('卖空条件（满足2个以上）:')
    print('  1. 顶部形态（双重顶/头肩顶/圆弧顶）')
    print('  2. 突破失败（突破后迅速回落）')
    print('  3. 量价背离（价格新高但成交量萎缩）')
    print('  4. RSI高位反转（RSI>70后快速下跌）')
    print('  5. 均线死叉（MA20下穿MA50）')
