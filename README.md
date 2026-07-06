![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![FIFA](https://img.shields.io/badge/FIFA-World_Cup_2026-darkred?style=for-the-badge&logo=fifa&logoColor=white)
![Quant](https://img.shields.io/badge/Quantitative-Analysis-blueviolet?style=for-the-badge)

# ⚽ Quant-JingCai — 量化竞彩分析引擎

> 🧠 用量化交易的思维方式，科学分析中国体育彩票竞彩足球。
> 
> 本项目将国际博彩市场（Pinnacle 平博）的赔率视为"真实概率"基准，通过数学模型去除抽水、计算期望值、优化仓位，为竞彩玩家提供**严格的统计套利决策支持**。

---

## ✨ 核心特性

| 模块 | 功能 | 技术 |
|------|------|------|
| 🔄 **双源数据抓取** | 实时抓取澳客网竞彩赔率 + Pinnacle 国际赔率 | Playwright + The Odds API |
| 🧮 **量化计算引擎** | 去水还原真实概率、EV 计算、凯利仓位 | Proportional Margin Removal |
| 🎯 **动量狙击信号** | 追踪赔率变动趋势，捕捉最佳下注时机 | SQLite 时间序列 + d(EV)/dt |
| 🧩 **M串N 优化器** | 多场次联合下注的线性规划资金分配 | Scipy Linear Programming |
| 📊 **实时仪表盘** | Web 可视化监控赔率变动与 EV 趋势 | Python HTTP Server + Chart.js |
| 🏆 **冠军概率追踪** | 基于 7 家博彩公司赔率的 Shin 模型概率计算 | Shin Model + 多源爬虫 |
| 📈 **历史回测研究** | Pinnacle 历史赔率 vs 实际结果的校准分析 | jokecamp/FootballData |

---

## 📁 项目结构

```
Quant-JingCai/
├── core/                              # 🔧 核心引擎
│   ├── main.py                        # 主引擎入口 (+EV 巡航模式)
│   ├── run_once.py                    # 单次扫描入口 (适合 cron)
│   ├── data_fetcher.py                # 双源数据抓取与对齐
│   ├── math_engine.py                 # 量化计算核心 (去水/EV/凯利)
│   ├── mn_optimizer.py                # M串N 线性规划优化器
│   ├── time_manager.py                # 时区管理与营业时间判定
│   └── storage.py                     # SQLite 赔率时间序列存储
│
├── research/                          # 🔬 研究分析工具
│   ├── implied_prob_comparator.py     # 小组赛 vs 淘汰赛隐含概率研究
│   ├── draw_odds_analyzer.py          # Pinnacle 平局赔率复盘报告
│   ├── github_data_analyzer.py        # 历史数据回测 (Pinnacle 校准)
│   ├── group_vs_knockout_analyzer.py  # 大样本赛段对比分析
│   ├── analyze_stages.py              # Shin 概率阶段趋势分析
│   └── fetch_wc_odds.py              # 世界杯赔率抓取工具
│
├── dashboard/                         # 📊 Web 实时仪表盘
│   ├── dashboard_server.py            # 后端服务 (读取 SQLite)
│   └── index.html                     # 前端页面 (Chart.js)
│
├── wc2026_predictions/                # 🏆 世界杯冠军概率追踪系统
│   ├── scraper_oddschecker.py         # Oddschecker 赔率爬虫
│   ├── scraper_oddspedia.py           # Oddspedia 赔率爬虫
│   ├── scraper_wettfreunde.py         # Wettfreunde 赔率爬虫
│   ├── update_processed_data.py       # Shin 模型核心处理引擎
│   ├── create_visualization.py        # 可视化图表生成
│   ├── run_all.py                     # 一键运行入口
│   ├── raw_data_during_wm/            # 原始赔率快照数据
│   ├── processed_data_during_wm/      # 处理后概率数据
│   └── single_games_predictions/      # 单场比赛预测
│
├── FootballData/                      # 📚 历史足球数据 (submodule)
└── worldcup/                          # 📚 世界杯历史数据 (submodule)
```

---

## 🚀 快速上手

### 1. 安装依赖

```bash
pip install -r requirements.txt

# 如果需要使用澳客网爬虫功能，还需安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置 API Key

```bash
cp config.example.json config.json
# 编辑 config.json，填入你的 The Odds API Key
# 免费申请地址: https://the-odds-api.com/
```

### 3. 运行

```bash
# 单次扫描 (推荐初次使用)
python -m core.run_once

# 持续巡航模式 (每 5 分钟自动轮询)
python -m core.main

# 启动 Web 仪表盘
python -m dashboard.dashboard_server
# 访问 http://localhost:8080

# 运行研究工具
python -m research.draw_odds_analyzer
python -m research.implied_prob_comparator

# 世界杯冠军概率追踪
cd wc2026_predictions && python run_all.py
```

---

## 🧮 核心算法

### 1. 比例去水法 (Proportional Margin Removal)

博彩公司的赔率包含了"抽水" (Margin/Overround)。Pinnacle 的抽水率通常只有 2-3%，是全球最低的。我们通过以下公式还原真实概率：

```
隐含概率 = 1 / 赔率
真实概率 = 隐含概率 / Σ(所有隐含概率)
```

### 2. 凯利准则 (Kelly Criterion)

在确认正期望 (+EV) 后，使用凯利公式计算最优下注比例：

```
f* = (b × p - q) / b

其中: b = 赔率 - 1, p = 真实概率, q = 1 - p
实际使用 1/4 Kelly (fraction=0.25) 以降低波动
```

### 3. Shin 模型 (Shin Probability Model)

用于冠军概率追踪。相比简单的去水法，Shin 模型考虑了"知情交易者"的影响，能更准确地从期货赔率中提取各队的真实夺冠概率。

### 4. 动量狙击 (Momentum Sniper)

追踪 EV 的时间序列变化率 d(EV)/dt：
- **EV 上升中** → HOLD（等待利润奔跑）
- **EV 拐头下降** → SNIPE!（拐点出现，立刻狙击下单）
- **EV 高位盘整** → STABLE（可随时建仓）

---

## 📐 铁律

1. **绝不下注负期望 (EV < 1.0) 的选项**
2. **单日总敞口上限 5%（硬性风控红线）**
3. **绝不使用 3串1 或更高串关** — 所有串关必须拆解为 2串1 矩阵
4. **严格使用 Fractional Kelly (1/4)** — 防止过度下注

---

## ⚠️ 免责声明

> 本项目仅供**学术研究和技术学习**使用。
> 
> 体育博彩存在风险，过往的统计分析不代表未来的结果。请遵守当地法律法规，理性参与，量力而行。
> 
> 作者不对因使用本项目而产生的任何经济损失承担责任。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

Copyright © 2026 [ywan4454](https://github.com/ywan4454)
