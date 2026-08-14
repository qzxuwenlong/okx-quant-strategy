# -*- coding: utf-8 -*-
"""
日本股票关键词配置
添加日经225成分股和知名日本股票
"""

# 日本股票关键词
JAPAN_STOCK_KEYWORDS = [
    # ========== 日经225核心成分股 ==========
    # 科技
    'SONY', 'NTT', 'SOFTBANK', 'KDDI', 'HITACHI', 'TOSHIBA', 'FUJITSU',
    'NEC', 'PANASONIC', 'SHARP', 'CANON', 'NIKON', 'OLYMPUS',
    
    # 汽车
    'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'SUBARU', 'SUZUKI',
    
    # 金融
    'MUFG', 'MIZUHO', 'SMFG', 'NOMURA', 'DAIWA',
    
    # 制造业
    'KOMATSU', 'KUBOTA', 'MITSUBISHI', 'SUMITOMO', 'ITOCHU',
    'MARUBENI', 'MITSUI', 'TOYOTA_TSUSHO',
    
    # 消费
    'FAST_RETAILING', 'UNIQLO', 'SEVEN_ELEVEN', 'FAMILYMART',
    'KIRIN', 'ASAHI', 'SUNTORY',
    
    # 医药
    'TAKEDA', 'ASTELLAS', 'DAIICHI_SANKYO', 'EISAI',
    
    # ========== 日本ETF ==========
    'EWJ',  # 日本ETF
    'DXJ',  # 日本对冲ETF
    
    # ========== 日经指数 ==========
    'NIKKEI',  # 日经225指数
    'TOPIX',   # 东证指数
]

# 日本股票特殊处理
# 注意：OKX上可能没有直接的日本股票永续合约
# 但可以通过以下方式获取：
# 1. 日经225指数期货
# 2. 日本ETF（如EWJ）
# 3. 或者使用其他数据源

print("日本股票关键词已加载")
print(f"共 {len(JAPAN_STOCK_KEYWORDS)} 个关键词")
