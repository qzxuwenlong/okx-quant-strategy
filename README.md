# OKX量化交易策略

基于欧奈尔+威科夫理论的加密货币/美股永续合约量化交易系统。

---

## 项目特点

- ✅ 简单有效的基础策略
- ✅ 市场扫描，自动找信号
- ✅ 仓位管理，控制风险
- ✅ 止盈止损，自动出场
- ✅ 交易日志，记录复盘
- ✅ 实时告警，不错过机会

---

## 策略表现

| 市场环境 | 策略收益 | 买入持有 |
|----------|----------|----------|
| 熊市 | +6.45% | -16.82% |
| 牛市 | +6.70% | +7.45% |
| 震荡 | 持平 | 持平 |

**核心优势：熊市保护出色，牛市接近持有收益**

---

## 快速开始

### 1. 安装依赖

`ash
pip install -r requirements.txt
`

### 2. 配置代理（可选）

编辑 config/settings.py：

`python
PROXY = 'http://127.0.0.1:7890'  # 你的代理地址
`

### 3. 运行扫描

`ash
python run.py
`

---

## 目录结构

`
okx-quant/
│
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   ├── strategies/        # 策略模块
│   └── utils/             # 工具模块
│
├── config/                 # 配置文件
├── data/                   # 数据文件
├── docs/                   # 文档
├── tests/                  # 测试
│
├── run.py                  # 主程序
├── requirements.txt        # 依赖包
└── README.md               # 说明文档
`

---

## 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 数据管理 | data_manager.py | 获取市场数据 |
| 信号生成 | signal_generator.py | 生成买卖信号 |
| 仓位管理 | position_manager.py | 计算仓位大小 |
| 告警系统 | alert_system.py | 实时通知 |
| 交易日志 | trade_journal.py | 记录交易 |

---

## 策略逻辑

### 入场条件
1. 趋势：价格 > 50日均线
2. RSI：25-65（不追高）
3. 成交量：> 1.2倍均量

### 出场条件
1. 止损：入场价 - ATR*2
2. 止盈：入场价 + ATR*4
3. RSI > 75（超买出场）

### 仓位管理
- 单笔风险：2%
- 单品种上限：20%
- 最大持仓：5个

---

## 使用示例

`python
from src.core import DataManager, SignalGenerator, PositionManager

# 初始化
dm = DataManager()
sg = SignalGenerator()
pm = PositionManager(capital=10000, risk=0.02)

# 获取数据
data = dm.fetch_klines('BTC-USDT-SWAP')

# 生成信号
indicators = sg.calculate_indicators(data['prices'], data['volumes'])
signal, score = sg.generate_signal(indicators)

# 计算仓位
if signal == 'buy':
    size = pm.calculate_size(entry_price, stop_loss)
`

---

## 配置说明

编辑 config/settings.py：

`python
# 资金配置
INITIAL_CAPITAL = 10000      # 初始资金
RISK_PER_TRADE = 0.02        # 单笔风险2%
MAX_POSITIONS = 5            # 最大持仓数

# 策略配置
MIN_SCORE = 4                # 最低信号得分
SCAN_INTERVAL = 300          # 扫描间隔（秒）

# 止盈止损
STOP_LOSS_ATR = 2            # 止损ATR倍数
TAKE_PROFIT_ATR = 4          # 止盈ATR倍数
`

---

## 文档

- [策略设计](docs/strategy_design.md)
- [仓位管理](docs/position_guide.md)
- [API指南](docs/api_guide.md)

---

## 注意事项

1. **风险提示**：加密货币交易风险极高
2. **模拟测试**：先用模拟资金测试
3. **代理配置**：确保网络连接正常
4. **API安全**：不要泄露API密钥

---

## 更新日志

### v1.0 (2026-08-11)
- 初始版本发布
- 基础策略实现
- 市场扫描功能
- 仓位管理系统
- 交易日志功能

---

## 许可证

MIT License

---

*最后更新：2026-08-11*
