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
│   └── ...                            # 多源爬虫与预测可视化
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
```

---

## ⚠️ 免责声明

> 本项目仅供**学术研究和技术学习**使用。
> 
> 体育博彩存在风险，过往的统计分析不代表未来的结果。请遵守当地法律法规，理性参与，量力而行。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。
