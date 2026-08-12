# -*- coding: utf-8 -*-
"""
更新US_STOCK_KEYWORDS，添加更多美股
"""

# 扩展的美股关键词列表
EXTENDED_US_STOCK_KEYWORDS = [
    # ========== 科技巨头 ==========
    'TSLA', 'AAPL', 'NVDA', 'META', 'GOOGL', 'AMZN', 'MSFT', 'NFLX',
    'CRM', 'ADBE', 'INTU', 'NOW', 'SNOW', 'PLTR', 'CRWD', 'ZS',
    'PANW', 'FTNT', 'OKTA', 'TWLO', 'NET', 'DDOG',
    
    # ========== 芯片半导体 ==========
    'AMD', 'INTC', 'QCOM', 'AVGO', 'TSM', 'ASML', 'MU', 'MRVL',
    'AMAT', 'LRCX', 'KLAC', 'TER', 'ON', 'TSEM', 'COHR', 'CGNX',
    
    # ========== 金融科技 ==========
    'COIN', 'HOOD', 'SQ', 'PYPL', 'V', 'MA', 'AXP', 'GS', 'MS',
    'JPM', 'BAC', 'WFC', 'C', 'BLK', 'SCHW',
    
    # ========== 中概股 ==========
    'PDD', 'BABA', 'JD', 'NIO', 'XPEV', 'LI', 'BIDU', 'NTES',
    'TME', 'IQ', 'BILI', 'MNSO', 'ZH', 'TAL',
    
    # ========== 消费品牌 ==========
    'COST', 'WMT', 'TGT', 'HD', 'LOW', 'NKE', 'LULU', 'SBUX',
    'MCD', 'YUM', 'CMG', 'DPZ',
    
    # ========== 医疗健康 ==========
    'UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT',
    'DHR', 'BMY', 'AMGN', 'GILD', 'ISRG', 'MDT', 'SYK', 'BSX',
    
    # ========== 工业制造 ==========
    'CAT', 'DE', 'HON', 'UPS', 'FDX', 'GE', 'MMM', 'EMR',
    'ITW', 'ETN', 'ROK', 'PH', 'CMI',
    
    # ========== 能源 ==========
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'OXY', 'VLO',
    'MPC', 'PSX', 'HES',
    
    # ========== 电信媒体 ==========
    'DIS', 'NFLX', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR', 'EA',
    'ATVI', 'TTWO', 'ROKU', 'PARA', 'WBD',
    
    # ========== ETF ==========
    'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'ARKK', 'XLF',
    'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB',
    'SOXX', 'SMH', 'IGV', 'FNGU', 'TQQQ', 'SQQQ', 'SOXL', 'SOXS',
    
    # ========== 其他知名 ==========
    'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'SOFI', 'AFRM', 'UPST',
    'DKNG', 'PENN', 'MGM', 'LVS', 'WYNN', 'CZR',
]

# 去重
EXTENDED_US_STOCK_KEYWORDS = sorted(list(set(EXTENDED_US_STOCK_KEYWORDS)))

print("=" * 60)
print(f"扩展后的美股关键词: {len(EXTENDED_US_STOCK_KEYWORDS)} 个")
print("=" * 60)
print()
for i, keyword in enumerate(EXTENDED_US_STOCK_KEYWORDS, 1):
    print(f"{i:3}. {keyword}")
    
print(f"\n" + "=" * 60)
print(f"总共 {len(EXTENDED_US_STOCK_KEYWORDS)} 个美股关键词")
print("=" * 60)
