# -*- coding: utf-8 -*-
"""
自动交易模块
连接OKX API执行交易
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import hmac
import hashlib
import base64
import json
from datetime import datetime

class OKXTrader:
    """OKX自动交易"""
    
    def __init__(self, api_key='', secret='', passphrase='', sandbox=True, proxy=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.sandbox = sandbox
        self.proxy = proxy
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # API地址
        if sandbox:
            self.base_url = 'https://www.okx.com'  # 模拟环境用同一个地址，通过header区分
        else:
            self.base_url = 'https://www.okx.com'
    
    def _sign(self, timestamp, method, path, body=''):
        """生成签名"""
        message = timestamp + method + path + body
        signature = hmac.new(
            self.secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def _headers(self, method, path, body=''):
        """生成请求头"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        sign = self._sign(timestamp, method, path, body)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        if self.sandbox:
            headers['x-simulated-trading'] = '1'
        
        return headers
    
    def get_balance(self):
        """获取账户余额"""
        path = '/api/v5/account/balance'
        headers = self._headers('GET', path)
        
        try:
            response = requests.get(
                self.base_url + path,
                headers=headers,
                proxies=self.proxies,
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == '0':
                return data['data'][0]
            else:
                print('获取余额失败: ' + str(data))
                return None
        except Exception as e:
            print('获取余额错误: ' + str(e))
            return None
    
    def get_positions(self):
        """获取持仓"""
        path = '/api/v5/account/positions'
        headers = self._headers('GET', path)
        
        try:
            response = requests.get(
                self.base_url + path,
                headers=headers,
                proxies=self.proxies,
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == '0':
                return data['data']
            else:
                print('获取持仓失败: ' + str(data))
                return []
        except Exception as e:
            print('获取持仓错误: ' + str(e))
            return []
    
    def place_order(self, symbol, side, size, price=None, stop_loss=None, take_profit=None):
        """
        下单
        
        Args:
            symbol: 交易对 (如 'TSLA-USDT-SWAP')
            side: 'buy' 或 'sell'
            size: 数量
            price: 限价（None=市价）
            stop_loss: 止损价
            take_profit: 止盈价
        """
        path = '/api/v5/trade/order'
        
        # 订单参数
        order_data = {
            'instId': symbol,
            'tdMode': 'cash',  # 现货模式
            'side': side,
            'ordType': 'market' if price is None else 'limit',
            'sz': str(size)
        }
        
        if price:
            order_data['px'] = str(price)
        
        body = json.dumps(order_data)
        headers = self._headers('POST', path, body)
        
        try:
            response = requests.post(
                self.base_url + path,
                headers=headers,
                data=body,
                proxies=self.proxies,
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == '0':
                order_id = data['data'][0]['ordId']
                print('下单成功: ' + symbol + ' ' + side + ' ' + str(size))
                print('订单ID: ' + order_id)
                
                # 设置止损止盈
                if stop_loss:
                    self.set_stop_loss(symbol, side, size, stop_loss)
                if take_profit:
                    self.set_take_profit(symbol, side, size, take_profit)
                
                return order_id
            else:
                print('下单失败: ' + str(data))
                return None
        except Exception as e:
            print('下单错误: ' + str(e))
            return None
    
    def set_stop_loss(self, symbol, side, size, stop_price):
        """设置止损"""
        path = '/api/v5/trade/order'
        
        # 止损方向与开仓相反
        sl_side = 'sell' if side == 'buy' else 'buy'
        
        order_data = {
            'instId': symbol,
            'tdMode': 'cash',
            'side': sl_side,
            'ordType': 'conditional',
            'sz': str(size),
            'slTriggerPx': str(stop_price),
            'slOrdPx': '-1'  # 市价
        }
        
        body = json.dumps(order_data)
        headers = self._headers('POST', path, body)
        
        try:
            response = requests.post(
                self.base_url + path,
                headers=headers,
                data=body,
                proxies=self.proxies,
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == '0':
                print('止损设置成功: ' + str(stop_price))
            else:
                print('止损设置失败: ' + str(data))
        except Exception as e:
            print('止损设置错误: ' + str(e))
    
    def set_take_profit(self, symbol, side, size, tp_price):
        """设置止盈"""
        path = '/api/v5/trade/order'
        
        # 止盈方向与开仓相反
        tp_side = 'sell' if side == 'buy' else 'buy'
        
        order_data = {
            'instId': symbol,
            'tdMode': 'cash',
            'side': tp_side,
            'ordType': 'conditional',
            'sz': str(size),
            'tpTriggerPx': str(tp_price),
            'tpOrdPx': '-1'  # 市价
        }
        
        body = json.dumps(order_data)
        headers = self._headers('POST', path, body)
        
        try:
            response = requests.post(
                self.base_url + path,
                headers=headers,
                data=body,
                proxies=self.proxies,
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == '0':
                print('止盈设置成功: ' + str(tp_price))
            else:
                print('止盈设置失败: ' + str(data))
        except Exception as e:
            print('止盈设置错误: ' + str(e))
    
    def close_position(self, symbol, side, size):
        """平仓"""
        close_side = 'sell' if side == 'buy' else 'buy'
        return self.place_order(symbol, close_side, size)


# 测试
if __name__ == '__main__':
    from config.settings import API_KEY, SECRET, PASSPHRASE, SANDBOX, PROXY
    
    trader = OKXTrader(
        api_key=API_KEY,
        secret=SECRET,
        passphrase=PASSPHRASE,
        sandbox=SANDBOX,
        proxy=PROXY
    )
    
    # 测试获取余额
    if API_KEY:
        print('测试连接...')
        balance = trader.get_balance()
        if balance:
            print('连接成功!')
            print('账户信息: ' + str(balance))
        else:
            print('连接失败，请检查API配置')
    else:
        print('请先配置API密钥: config/api_keys.py')
