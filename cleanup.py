# -*- coding: utf-8 -*-
"""清理项目文件"""

import os
import shutil

base = "D:\\xm\\quanke11"

# ============== 文件分类 ==============

# 核心文件（保留）
KEEP_FILES = [
    'run.py',
    'README.md',
    'PROJECT_STRUCTURE.md',
    'requirements.txt',
    '.gitignore',
]

# 需要移动到src/的文件
MOVE_TO_SRC = {
    'auto_trading_system.py': 'src/core/auto_trading.py',
    'backtester.py': 'src/strategies/backtester.py',
    'alert_system.py': 'src/core/alert_system.py',
    'position_manager.py': 'src/core/position_manager.py',
    'trade_journal.py': 'src/utils/trade_journal.py',
}

# 需要移动到docs/的文档
MOVE_TO_DOCS = [
    '项目总结.md',
    'strategy_design.md',
    '仓位管理说明.md',
    '周期与持仓说明.md',
    '牛熊判断速查表.md',
    '欧奈尔vs马克斯_牛熊判断.md',
    '策略功能总结.md',
    '策略优化清单.md',
    '待办清单.md',
    '快速启动指南.md',
    '重要说明.md',
    '系统检查报告.md',
]

# 可以删除的文件（测试/调试/历史版本）
DELETE_FILES = [
    # 测试文件
    'test_exit.py',
    'test_exit2.py',
    'test_journal.json',
    'test_proxy_connection.py',
    'test_public_data.py',
    'test_scan_debug.py',
    'test_simple.py',
    'test_usdt_perp.py',
    'debug_scan.py',
    'debug_scan2.py',
    
    # 重复的扫描器
    'scanner.py',
    'scanner_direct.py',
    'scanner_final.py',
    
    # 重复的策略文件
    'strategy_example.py',
    'strategy_v1_final.py',
    
    # 测试版本策略
    'enhanced_backtester.py',
    'optimized_strategy.py',
    'optimized_strategy_v2.py',
    'ultimate_strategy.py',
    'final_optimized.py',
    
    # 重复的系统文件
    'complete_system.py',
    'final_system.py',
    'trading_system.py',
    
    # 测试脚本
    'calculate_annual.py',
    'compare_strategies.py',
    'fair_comparison.py',
    'long_term_compare.py',
    
    # 高级功能（暂不需要）
    'multi_timeframe.py',
    'sentiment_indicators.py',
    'market_regime_detector.py',
    'combined_regime_detector.py',
    'exit_strategy.py',
    'visualize_regime.py',
    
    # 示例文件
    'example_combined_regime.py',
    'example_market_regime.py',
    
    # 重复的运行脚本
    'run_auto_system.py',
    'run_scan.py',
]

def cleanup():
    print("=" * 60)
    print("项目文件清理")
    print("=" * 60)
    
    # 1. 移动核心文件到src/
    print("\n[1] 移动核心文件到src/")
    print("-" * 40)
    for src_file, dst_file in MOVE_TO_SRC.items():
        src_path = os.path.join(base, src_file)
        dst_path = os.path.join(base, dst_file)
        
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)
            print(f"  移动: {src_file} -> {dst_file}")
        else:
            print(f"  跳过: {src_file} (不存在)")
    
    # 2. 移动文档到docs/
    print("\n[2] 移动文档到docs/")
    print("-" * 40)
    for doc_file in MOVE_TO_DOCS:
        src_path = os.path.join(base, doc_file)
        dst_path = os.path.join(base, 'docs', doc_file)
        
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)
            print(f"  移动: {doc_file} -> docs/{doc_file}")
        else:
            print(f"  跳过: {doc_file} (不存在)")
    
    # 3. 删除不需要的文件
    print("\n[3] 删除不需要的文件")
    print("-" * 40)
    deleted = 0
    for del_file in DELETE_FILES:
        file_path = os.path.join(base, del_file)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  删除: {del_file}")
            deleted += 1
        else:
            print(f"  跳过: {del_file} (不存在)")
    
    print(f"\n  共删除 {deleted} 个文件")
    
    # 4. 显示最终结构
    print("\n" + "=" * 60)
    print("清理完成！最终目录结构:")
    print("=" * 60)
    
    for root, dirs, files in os.walk(base):
        # 跳过隐藏目录和__pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'backup']
        
        level = root.replace(base, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files)[:10]:  # 只显示前10个文件
            print(f"{subindent}{file}")
        
        if len(files) > 10:
            print(f"{subindent}... 还有 {len(files) - 10} 个文件")

if __name__ == "__main__":
    cleanup()
