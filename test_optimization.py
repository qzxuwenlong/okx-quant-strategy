# -*- coding: utf-8 -*-
"""
策略优化测试框架
每次只改一个变量，回测对比
"""

import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from src.strategies.backtester import Backtester, format_report
from src.core.signal_generator import SignalGenerator

class OptimizationTester:
    """优化测试器"""
    
    def __init__(self):
        self.results_history = []
    
    def run_backtest(self, name, backtester_class, symbol='SPY-USDT-SWAP'):
        """运行回测并记录结果"""
        bt = backtester_class(initial_capital=10000)
        results = bt.run_backtest_new(symbol)
        
        if results:
            self.results_history.append({
                'name': name,
                'total_return': results['total_return'],
                'win_rate': results['win_rate'],
                'profit_factor': results['profit_factor'],
                'max_drawdown': results['max_drawdown'],
                'total_trades': results['total_trades']
            })
            return results
        return None
    
    def compare_results(self):
        """对比所有测试结果"""
        if not self.results_history:
            print("没有测试结果")
            return
        
        print("\n" + "=" * 80)
        print("优化对比测试")
        print("=" * 80)
        
        # 表头
        print("{:<25} {:<12} {:<10} {:<12} {:<12} {:<10}".format(
            "策略", "总收益", "胜率", "盈亏比", "最大回撤", "交易数"))
        print("-" * 80)
        
        # 每行数据
        baseline = self.results_history[0]
        for r in self.results_history:
            # 计算相对变化
            ret_change = r['total_return'] - baseline['total_return']
            win_change = r['win_rate'] - baseline['win_rate']
            
            # 标记改进/退步
            ret_mark = "↑" if ret_change > 0 else "↓" if ret_change < 0 else "="
            win_mark = "↑" if win_change > 0 else "↓" if win_change < 0 else "="
            
            print("{:<25} {:<12} {:<10} {:<12} {:<12} {:<10}".format(
                r['name'],
                f"{r['total_return']:.2f}%",
                f"{r['win_rate']:.2f}%",
                f"{r['profit_factor']:.2f}",
                f"{r['max_drawdown']:.2f}%",
                r['total_trades']
            ))
        
        print("-" * 80)
        
        # 最佳策略
        best = max(self.results_history, key=lambda x: x['total_return'])
        print(f"\n最佳策略: {best['name']} (收益: {best['total_return']:.2f}%)")

# 测试函数
def test_original():
    """测试原始策略"""
    from run_backtest_new import NewBacktester
    return NewBacktester

# 运行测试
if __name__ == '__main__':
    tester = OptimizationTester()
    
    # 测试原始策略（基准）
    print("=" * 60)
    print("测试基准策略（当前版本）")
    print("=" * 60)
    bt_class = test_original()
    tester.run_backtest("基准策略", bt_class)
    
    # 显示对比
    tester.compare_results()
