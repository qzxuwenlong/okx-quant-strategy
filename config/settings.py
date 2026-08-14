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
# 可选: 'all', 'us_stocks', 'crypto', 'japan', 'mixed'
MARKET_FILTER = 'mixed'

# 美股关键词
US_STOCK_KEYWORDS = [
    # 科技巨头
    'TSLA', 'AAPL', 'NVDA', 'META', 'GOOGL', 'AMZN', 'MSFT', 'NFLX',
    'CRM', 'ADBE', 'INTU', 'NOW', 'SNOW', 'PLTR', 'CRWD', 'ZS',
    'PANW', 'FTNT', 'OKTA', 'TWLO', 'NET', 'DDOG',
    
    # 芯片半导体
    'AMD', 'INTC', 'QCOM', 'AVGO', 'TSM', 'ASML', 'MU', 'MRVL',
    'AMAT', 'LRCX', 'KLAC', 'TER', 'ON', 'TSEM', 'COHR', 'CGNX',
    
    # 金融科技
    'COIN', 'HOOD', 'SQ', 'PYPL', 'V', 'MA', 'AXP', 'GS', 'MS',
    'JPM', 'BAC', 'WFC', 'C', 'BLK', 'SCHW',
    
    # 中概股
    'PDD', 'BABA', 'JD', 'NIO', 'XPEV', 'LI', 'BIDU', 'NTES',
    'TME', 'IQ', 'BILI', 'MNSO', 'ZH', 'TAL',
    
    # 消费品牌
    'COST', 'WMT', 'TGT', 'HD', 'LOW', 'NKE', 'LULU', 'SBUX',
    'MCD', 'YUM', 'CMG', 'DPZ',
    
    # 医疗健康
    'UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT',
    'DHR', 'BMY', 'AMGN', 'GILD', 'ISRG', 'MDT', 'SYK', 'BSX',
    
    # 工业制造
    'CAT', 'DE', 'HON', 'UPS', 'FDX', 'GE', 'MMM', 'EMR',
    'ITW', 'ETN', 'ROK', 'PH', 'CMI',
    
    # 能源
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'OXY', 'VLO',
    'MPC', 'PSX', 'HES',
    
    # 电信媒体
    'DIS', 'NFLX', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR', 'EA',
    'ATVI', 'TTWO', 'ROKU', 'PARA', 'WBD',
    
    # ETF
    'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'ARKK', 'XLF',
    'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB',
    'SOXX', 'SMH', 'IGV', 'FNGU', 'TQQQ', 'SQQQ', 'SOXL', 'SOXS',
    
    # 其他
    'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'SOFI', 'AFRM', 'UPST',
    'DKNG', 'PENN', 'MGM', 'LVS', 'WYNN', 'CZR',
]

# 日本股票关键词
JAPAN_STOCK_KEYWORDS = [
    # 日本ETF
    'EWJ',   # 日本ETF
    'DXJ',   # 日本对冲ETF
    
    # 日经指数
    'NIKKEI',
    'TOPIX',
    
    # 日本知名公司（如果OKX有）
    'SONY', 'TOYOTA', 'HONDA', 'SOFTBANK', 'NINTENDO',
]

# 合并所有关键词
ALL_STOCK_KEYWORDS = US_STOCK_KEYWORDS + JAPAN_STOCK_KEYWORDS

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
SANDBOX = False  # True=模拟环境, False=实盘

# ============== 策略选择 ==============
# 可选: 'western' (欧奈尔+威科夫), 'japanese' (日本蜡烛图+cis/BNF), 'combined' (综合)
STRATEGY_TYPE = 'combined'
