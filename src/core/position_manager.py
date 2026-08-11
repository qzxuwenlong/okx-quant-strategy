# -*- coding: utf-8 -*-
"""
仓位管理模块
基于风险、波动率、账户资金的仓位计算
"""

import numpy as np

class PositionManager:
    """仓位管理器"""
    
    def __init__(self, total_capital=10000, max_risk_per_trade=0.02, max_positions=5):
        """
        初始化仓位管理器
        
        Args:
            total_capital: 总资金 (USDT)
            max_risk_per_trade: 单笔最大风险 (默认2%)
            max_positions: 最大持仓数量
        """
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_positions = max_positions
        self.positions = {}  # 当前持仓
    
    def calculate_position_size(self, entry_price, stop_loss, signal_type='buy'):
        """
        计算仓位大小（基于风险）
        
        Args:
            entry_price: 入场价
            stop_loss: 止损价
            signal_type: 信号类型 ('buy' 或 'short')
            
        Returns:
            dict: 仓位信息
        """
        # 计算单笔风险金额
        risk_amount = self.total_capital * self.max_risk_per_trade
        
        # 计算止损距离
        if signal_type == 'buy':
            risk_per_unit = entry_price - stop_loss
        else:  # short
            risk_per_unit = stop_loss - entry_price
        
        if risk_per_unit <= 0:
            return {'error': '止损价设置错误'}
        
        # 计算仓位数量
        position_size = risk_amount / risk_per_unit
        
        # 计算仓位价值
        position_value = position_size * entry_price
        
        # 检查是否超过总资金的20%
        max_position_value = self.total_capital * 0.20
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
            position_value = max_position_value
        
        # 计算实际风险
        actual_risk = position_size * risk_per_unit
        actual_risk_pct = actual_risk / self.total_capital * 100
        
        return {
            'position_size': round(position_size, 4),
            'position_value': round(position_value, 2),
            'risk_amount': round(actual_risk, 2),
            'risk_pct': round(actual_risk_pct, 2),
            'stop_loss': stop_loss,
            'entry_price': entry_price
        }
    
    def calculate_scaled_position(self, entry_price, stop_loss, atr, signal_strength='normal'):
        """
        根据信号强度调整仓位
        
        Args:
            entry_price: 入场价
            stop_loss: 止损价
            atr: ATR值
            signal_strength: 信号强度 ('weak', 'normal', 'strong')
        """
        # 基础仓位
        base_result = self.calculate_position_size(entry_price, stop_loss)
        
        if 'error' in base_result:
            return base_result
        
        # 信号强度系数
        strength_multiplier = {
            'weak': 0.5,      # 弱信号：半仓
            'normal': 1.0,    # 正常：全仓
            'strong': 1.5     # 强信号：1.5倍
        }
        
        multiplier = strength_multiplier.get(signal_strength, 1.0)
        
        # 调整仓位
        adjusted_size = base_result['position_size'] * multiplier
        
        # 波动率调整（ATR越大，仓位越小）
        atr_pct = atr / entry_price
        if atr_pct > 0.05:  # 高波动
            adjusted_size *= 0.7
        elif atr_pct < 0.02:  # 低波动
            adjusted_size *= 1.2
        
        # 重新计算
        adjusted_value = adjusted_size * entry_price
        risk_per_unit = abs(entry_price - stop_loss)
        adjusted_risk = adjusted_size * risk_per_unit
        
        return {
            'position_size': round(adjusted_size, 4),
            'position_value': round(adjusted_value, 2),
            'risk_amount': round(adjusted_risk, 2),
            'risk_pct': round(adjusted_risk / self.total_capital * 100, 2),
            'signal_strength': signal_strength,
            'multiplier': multiplier
        }
    
    def add_position(self, symbol, entry_price, position_size, position_type='long'):
        """添加持仓记录"""
        self.positions[symbol] = {
            'entry_price': entry_price,
            'size': position_size,
            'type': position_type,
            'value': round(entry_price * position_size, 2),
            'unrealized_pnl': 0
        }
        return self.positions[symbol]
    
    def update_pnl(self, symbol, current_price):
        """更新浮动盈亏"""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        if pos['type'] == 'long':
            pos['unrealized_pnl'] = round((current_price - pos['entry_price']) * pos['size'], 2)
        else:
            pos['unrealized_pnl'] = round((pos['entry_price'] - current_price) * pos['size'], 2)
        
        pos['unrealized_pnl_pct'] = round(pos['unrealized_pnl'] / pos['value'] * 100, 2)
        
        return pos
    
    def get_portfolio_summary(self):
        """获取持仓汇总"""
        total_value = sum(p['value'] for p in self.positions.values())
        total_pnl = sum(p['unrealized_pnl'] for p in self.positions.values())
        
        return {
            'total_positions': len(self.positions),
            'total_value': round(total_value, 2),
            'total_pnl': round(total_pnl, 2),
            'available_capital': round(self.total_capital - total_value, 2),
            'position_ratio': round(total_value / self.total_capital * 100, 2)
        }
    
    def can_open_position(self):
        """检查是否可以开新仓"""
        if len(self.positions) >= self.max_positions:
            return False, '持仓数量已达上限'
        
        summary = self.get_portfolio_summary()
        if summary['position_ratio'] > 80:
            return False, '仓位比例过高'
        
        return True, '可以开仓'
    
    def scale_in(self, symbol, add_price, add_size):
        """加仓"""
        if symbol not in self.positions:
            return {'error': '无持仓，无法加仓'}
        
        pos = self.positions[symbol]
        
        # 计算新的平均成本
        total_cost = pos['entry_price'] * pos['size'] + add_price * add_size
        new_size = pos['size'] + add_size
        new_avg_price = total_cost / new_size
        
        # 更新持仓
        pos['entry_price'] = round(new_avg_price, 4)
        pos['size'] = round(new_size, 4)
        pos['value'] = round(new_avg_price * new_size, 2)
        
        return {
            'symbol': symbol,
            'new_avg_price': round(new_avg_price, 4),
            'new_size': round(new_size, 4),
            'new_value': round(new_avg_price * new_size, 2)
        }
    
    def scale_out(self, symbol, reduce_size):
        """减仓"""
        if symbol not in self.positions:
            return {'error': '无持仓'}
        
        pos = self.positions[symbol]
        
        if reduce_size > pos['size']:
            return {'error': '减仓数量超过持仓'}
        
        new_size = pos['size'] - reduce_size
        pos['size'] = round(new_size, 4)
        pos['value'] = round(pos['entry_price'] * new_size, 2)
        
        # 如果全部减完，删除持仓
        if new_size <= 0:
            del self.positions[symbol]
            return {'symbol': symbol, 'action': 'closed'}
        
        return {
            'symbol': symbol,
            'remaining_size': round(new_size, 4),
            'remaining_value': round(pos['entry_price'] * new_size, 2)
        }


def format_position_report(manager, symbol=None, entry_price=None, stop_loss=None, atr=None):
    """生成仓位报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("仓位管理报告")
    lines.append("=" * 60)
    
    # 账户信息
    lines.append("总资金: $" + str(round(manager.total_capital, 2)))
    lines.append("单笔风险: " + str(manager.max_risk_per_trade*100) + "%")
    lines.append("最大持仓: " + str(manager.max_positions) + " 个")
    lines.append("-" * 60)
    
    # 如果提供了具体交易信息
    if entry_price and stop_loss:
        lines.append("")
        lines.append("【仓位计算】")
        lines.append("入场价: $" + str(round(entry_price, 2)))
        lines.append("止损价: $" + str(round(stop_loss, 2)))
        
        # 基础仓位
        basic = manager.calculate_position_size(entry_price, stop_loss)
        lines.append("")
        lines.append("基础仓位:")
        lines.append("  数量: " + str(basic['position_size']))
        lines.append("  价值: $" + str(round(basic['position_value'], 2)))
        lines.append("  风险: $" + str(round(basic['risk_amount'], 2)) + " (" + str(round(basic['risk_pct'], 1)) + "%)")
        
        # 不同信号强度
        if atr:
            lines.append("")
            lines.append("信号强度调整 (ATR=" + str(round(atr, 2)) + "):")
            for strength in ['weak', 'normal', 'strong']:
                result = manager.calculate_scaled_position(entry_price, stop_loss, atr, strength)
                lines.append("  " + strength.rjust(8) + ": " + str(result['position_size']).rjust(8) + " 数量 | $" + str(round(result['position_value'], 2)).rjust(10) + " 价值 | " + str(round(result['risk_pct'], 1)) + "% 风险")
    
    # 当前持仓
    if manager.positions:
        lines.append("")
        lines.append("【当前持仓】")
        lines.append("-" * 60)
        for sym, pos in manager.positions.items():
            pnl = pos.get('unrealized_pnl', 0)
            pnl_sign = '+' if pnl >= 0 else '-'
            lines.append("  " + sym.ljust(20) + " " + str(pos['size']).rjust(8) + " 数量 | $" + str(round(pos['value'], 2)).rjust(10) + " | PnL: " + pnl_sign + "$" + str(abs(pnl)))
    
    # 汇总
    summary = manager.get_portfolio_summary()
    lines.append("")
    lines.append("【汇总】")
    lines.append("-" * 60)
    lines.append("持仓数量: " + str(summary['total_positions']) + "/" + str(manager.max_positions))
    lines.append("持仓价值: $" + str(round(summary['total_value'], 2)))
    lines.append("可用资金: $" + str(round(summary['available_capital'], 2)))
    lines.append("仓位比例: " + str(round(summary['position_ratio'], 1)) + "%")
    lines.append("浮动盈亏: $" + str(round(summary['total_pnl'], 2)))
    
    lines.append("=" * 60)
    
    return '\n'.join(lines)


# 使用示例
if __name__ == "__main__":
    # 创建仓位管理器
    pm = PositionManager(
        total_capital=10000,      # 1万USDT
        max_risk_per_trade=0.02,  # 单笔2%风险
        max_positions=5           # 最多5个持仓
    )
    
    # 计算AMZN仓位
    entry = 277.81
    stop = 275.91
    atr = 1.9
    
    print(format_position_report(pm, 'AMZN', entry, stop, atr))
