# -*- coding: utf-8 -*-
"""
系统配置
"""

# ============== 网络配置 ==============
PROXY = 'http://127.0.0.1:7890'  # 代理地址

# ============== 资金配置 ==============
INITIAL_CAPITAL = 10000          # 初始资金
RISK_PER_TRADE = 0.02            # 单笔风险2%
MAX_POSITIONS = 5                # 最大持仓数

# ============== 策略配置 ==============
MIN_SCORE = 4                    # 最低信号得分
SCAN_INTERVAL = 300              # 扫描间隔（秒）

# ============== 交易品种 ==============
# 可选: 'all'（全部）, 'us_stocks'（美股）, 'crypto'（加密货币）
MARKET_FILTER = 'us_stocks'

# 美股关键词（用于从OKX自动筛选）
# 这些是知名的美股/港股/ETF，OKX会提供对应的永续合约
US_STOCK_KEYWORDS = [
    # 科技巨头
    'TSLA', 'AAPL', 'NVDA', 'META', 'GOOGL', 'AMZN', 'MSFT', 'NFLX',
    # 芯片
    'AMD', 'INTC', 'QCOM', 'AVGO', 'TSM',
    # 金融科技
    'COIN', 'HOOD', 'SQ', 'PYPL',
    # 中概股
    'PDD', 'BABA', 'JD', 'NIO', 'XPEV', 'LI', 'BIDU',
    # 其他知名
    'PLTR', 'CRWD', 'ADBE', 'GME', 'AMC',
    # ETF
    'SPY', 'QQQ', 'IWM',
]

# ============== 止盈止损 ==============
STOP_LOSS_ATR = 2                # 止损ATR倍数
TAKE_PROFIT_ATR = 4              # 止盈ATR倍数

# ============== API配置 ==============
try:
    from config.api_keys import API_KEY, SECRET, PASSPHRASE, ENABLE_AUTO_TRADE
except ImportError:
    API_KEY = ''
    SECRET = ''
    PASSPHRASE = ''
    ENABLE_AUTO_TRADE = False

# ============== 交易环境 ==============
SANDBOX = True  # True=模拟环境, False=实盘
