# OKX量化策略项目 - 目录结构

## 项目目录

`
D:\xm\quanke11\
│
├── src/                          # 源代码
│   ├── core/                     # 核心模块
│   │   ├── data_manager.py       # 数据获取
│   │   ├── signal_generator.py   # 信号生成
│   │   ├── position_manager.py   # 仓位管理
│   │   └── alert_system.py       # 告警系统
│   │
│   ├── strategies/               # 策略模块
│   │   ├── strategy_v1.py        # 基础版策略
│   │   ├── backtester.py         # 回测系统
│   │   └── scanner.py            # 市场扫描
│   │
│   └── utils/                    # 工具模块
│       ├── trade_journal.py      # 交易日志
│       └── helpers.py            # 辅助函数
│
├── config/                       # 配置文件
│   ├── settings.py               # 系统配置
│   └── api_keys.py               # API密钥（不提交）
│
├── data/                         # 数据文件
│   ├── logs/                     # 运行日志
│   └── trades/                   # 交易记录
│
├── docs/                         # 文档
│   ├── README.md                 # 项目说明
│   ├── strategy_design.md        # 策略设计
│   ├── position_guide.md         # 仓位指南
│   └── api_guide.md              # API指南
│
├── tests/                        # 测试文件
│   ├── test_strategy.py          # 策略测试
│   └── test_data.py              # 数据测试
│
├── backup/                       # 备份文件
│
├── run.py                        # 主运行脚本
├── requirements.txt              # 依赖包
└── .gitignore                    # Git忽略文件
`

---

## 核心文件说明

### 入口文件
| 文件 | 用途 |
|------|------|
| run.py | 主程序入口 |

### 核心模块 (src/core/)
| 文件 | 用途 |
|------|------|
| data_manager.py | 获取OKX市场数据 |
| signal_generator.py | 生成买卖信号 |
| position_manager.py | 仓位计算和管理 |
| alert_system.py | 实时告警通知 |

### 策略模块 (src/strategies/)
| 文件 | 用途 |
|------|------|
| strategy_v1.py | 基础版策略（最终版） |
| backtester.py | 历史回测 |
| scanner.py | 市场扫描 |

### 工具模块 (src/utils/)
| 文件 | 用途 |
|------|------|
| trade_journal.py | 交易日志记录 |

### 配置文件 (config/)
| 文件 | 用途 |
|------|------|
| settings.py | 系统参数配置 |
| api_keys.py | API密钥配置 |

---

## 运行方式

`ash
# 运行主程序
py run.py

# 运行市场扫描
py src/strategies/scanner.py

# 运行回测
py src/strategies/backtester.py

# 运行测试
py tests/test_strategy.py
`

---

## 当前文件（待整理）

以下文件在根目录，需要移动到对应目录：

### 核心文件
- auto_trading_system.py → src/core/
- strategy_v1_final.py → src/strategies/strategy_v1.py
- backtester.py → src/strategies/
- alert_system.py → src/core/
- position_manager.py → src/core/
- trade_journal.py → src/utils/

### 文档文件
- 项目总结.md → docs/
- 策略设计.md → docs/strategy_design.md
- 仓位管理说明.md → docs/position_guide.md

### 测试文件
- fair_comparison.py → tests/
- optimized_strategy*.py → tests/

### 历史文件（可删除）
- debug_*.py
- test_*.py
- scanner*.py
- enhanced_*.py

---

## Git忽略文件

`
# API密钥
config/api_keys.py

# 数据文件
data/
*.json
*.csv

# 编译文件
__pycache__/
*.pyc

# IDE
.vscode/
.idea/
`

---

## 快速开始

1. 配置API密钥（可选）
`python
# config/api_keys.py
API_KEY = 'your_api_key'
SECRET = 'your_secret'
PASSPHRASE = 'your_passphrase'
`

2. 运行扫描
`ash
py run.py
`

3. 查看结果
- 控制台输出信号
- data/trades/ 交易记录
- data/logs/ 运行日志

---

*最后更新：2026-08-11*
