# Quant-JingCai: Quantitative Sports Betting Engine

![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![FIFA](https://img.shields.io/badge/FIFA-World_Cup_2026-darkred.svg)
![Contributor](https://img.shields.io/badge/Contributor-@ywan4454-blueviolet.svg)

> A scientific, quantitative analysis engine for sports lottery betting, treating highly liquid international betting markets (e.g., Pinnacle) as the "true probability" benchmark.

## System Architecture

The project extracts true probabilities from international markets and compares them against domestic sports lottery odds to identify statistical arbitrage opportunities, executing strict risk management and bankroll allocation.

## Core Features

### [1] Dual-Source Data Fetching
- Real-time scraping of domestic lottery odds and Pinnacle international odds.
- Powered by Playwright (for dynamic DOM extraction) and The Odds API.

### [2] Quantitative Engine
- Proportional Margin Removal: Strips the bookmaker's margin to reveal true implied probabilities.
- EV Calculation: Calculates Expected Value to filter out negative EV bets.
- Kelly Criterion: Optimizes position sizing to protect the baseline bankroll.

### [3] Momentum Sniper
- Tracks historical odds movements via SQLite time-series data.
- Calculates d(EV)/dt to capture the optimal betting window before odds drop.

### [4] M*N Optimizer
- Resolves multi-match combination betting constraints using Scipy Linear Programming.

### [5] Live Dashboard
- Real-time web visualization of odds movements and EV trends via a Python HTTP Server and Chart.js.

## Project Structure

```text
Quant-JingCai/
├── core/                              # Core Engine
│   ├── main.py                        # Cruise mode (+EV loop)
│   ├── run_once.py                    # Single scan (cron-friendly)
│   ├── data_fetcher.py                # Dual-source fetch & align
│   ├── math_engine.py                 # Margin removal / EV / Kelly
│   ├── mn_optimizer.py                # M*N Linear Programming
│   ├── time_manager.py                # Timezone & market hours
│   └── storage.py                     # SQLite time-series storage
├── research/                          # Research & Tools
│   ├── implied_prob_comparator.py     # Group vs Knockout analysis
│   └── ...                            
├── dashboard/                         # Live Web Dashboard
└── FootballData/                      # Submodules
```

## Deployment

```bash
pip install -r requirements.txt
playwright install chromium

# Configure API Key
cp config.example.json config.json
# Edit config.json with your The Odds API Key

# Single scan
python -m core.run_once

# Continuous cruise mode
python -m core.main
```

## Contributors

* Core Architect / Quant Developer: [@ywan4454](https://github.com/ywan4454)

---
Disclaimer: This project is for academic research and technical learning only. Sports betting carries financial risk. Past statistical analysis does not guarantee future results. Please comply with local laws and gamble responsibly.
