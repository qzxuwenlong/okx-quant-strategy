# -*- coding: utf-8 -*-
"""
数据管理模块
获取OKX市场数据
"""

import requests
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import PROXY

class DataManager:
    def __init__(self, proxy=None):
        self.proxy = proxy or PROXY
        self.proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
    
    def fetch_klines(self, symbol, bar='4H', limit=200):
        """获取K线数据"""
        try:
            url = "https://www.okx.com/api/v5/market/candles"
            params = {"instId": symbol, "bar": bar, "limit": str(limit)}
            response = requests.get(url, params=params, proxies=self.proxies, timeout=10)
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                rows = data['data']
                prices = [float(row[4]) for row in rows][::-1]
                volumes = [float(row[5]) for row in rows][::-1]
                return {'prices': prices, 'volumes': volumes}
        except Exception as e:
            print("获取数据失败: " + str(e))
        return None
    
    def get_all_symbols(self):
        """获取所有USDT永续合约"""
        try:
            url = "https://www.okx.com/api/v5/public/instruments"
            params = {"instType": "SWAP"}
            response = requests.get(url, params=params, proxies=self.proxies, timeout=30)
            data = response.json()
            
            if data.get('code') == '0':
                return [inst['instId'] for inst in data['data'] 
                       if inst.get('settleCcy') == 'USDT' and inst.get('state') == 'live']
        except:
            pass
        return []
