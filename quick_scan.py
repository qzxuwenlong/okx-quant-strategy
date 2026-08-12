# -*- coding: utf-8 -*-
"""直接运行扫描测试"""

import sys
sys.path.insert(0, '.')

from src.strategies.scanner import MarketScanner

scanner = MarketScanner()
results = scanner.scan()
scanner.display(results)
