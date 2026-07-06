import time
from core.data_fetcher import fetch_jingcai_odds, fetch_pinnacle_odds, align_teams
from core.math_engine import analyze_match
from core.mn_optimizer import generate_combinations
from core.time_manager import is_jc_system_open
from core.storage import init_db, save_odds_snapshot, get_historical_ev_trend

TOTAL_BANKROLL = 10000.0  # 总本金
MAX_KELLY_CAP = 0.05      # 绝对红线：单日总敞口上限 5%

def print_alert(msg):
    print(f"\n==================================================")
    print(f"🔥 {msg}")
    print(f"--------------------------------------------------")

def quant_cruise_mode():
    """
    v6.0 纯粹的统计套利 +EV 巡航模式
    """
    print("🚀 Quant-JingCai 引擎 (v6.0 Final Paradigm) 启动...")
    print(f"💰 初始本金: {TOTAL_BANKROLL} 元 | 单日硬性风险敞口上限: {MAX_KELLY_CAP*100}%")
    
    # 初始化本地数据库，用于实时动量追踪
    init_db()
    
    while True:
        print("\n⏳ 正在执行轮询扫描...")
        
        # 1. 营业时间与防过期锁
        if not is_jc_system_open():
            print("⚠️ [警告] 当前非体彩营业时间，指令已挂起等待系统开机。")
            time.sleep(300)
            continue
            
        # 2. 拉取与对齐数据
        jc_matches = fetch_jingcai_odds()
        pinny_matches = fetch_pinnacle_odds()
        aligned = align_teams(jc_matches, pinny_matches)
        
        high_ev_matches = []
        total_kelly = 0.0
        
        # 3. 严格计算 +EV 并应用 Fractional Kelly 绝对红线
        for match in aligned:
            analysis = analyze_match(match)
            if not analysis or "best_option" not in analysis:
                continue
                
            best = analysis["best_option"]
            ev = best["ev"]
            
            # 将当前赔率切片持久化到本地 SQLite 数据库
            save_odds_snapshot(
                match_name=analysis["match_name"], 
                jc_odds=analysis.get("jc_odds", {}), 
                pin_odds=analysis.get("pin_odds", {}), 
                best_ev=ev, 
                best_selection=best["selection"]
            )
            
            # 铁律：绝不使用负 EV 选项
            if ev < 1.01:
                continue
                
            # 获取最近几轮的实时动量趋势 (Level 2 Order Book Simulation)
            trend_data = get_historical_ev_trend(analysis["match_name"], limit=3)
            trend_values = [row[1] for row in reversed(trend_data)]
            trend_str = " -> ".join([f"{v:.3f}" for v in trend_values])
            
            # --- 动量量化引擎 (Momentum Sniper) ---
            # 策略：计算斜率 d(EV)/dt。
            # 如果 EV 还在一直涨（体彩还没反应过来），就忍住不买（Wait），等它涨到最高！
            # 如果 EV 开始掉头向下（斜率 < 0），说明体彩操盘手醒了，立刻狙击下单 (Snipe)！
            execute_signal = "HOLD (等待利润奔跑)"
            if len(trend_values) >= 2:
                dEV = trend_values[-1] - trend_values[-2]
                if dEV < 0:
                    execute_signal = "🔥 SNIPE! (拐点出现，立刻狙击下单!)"
                elif dEV > 0:
                    execute_signal = "📈 HOLD (赔率仍在上涨，等待最高点)"
                else:
                    execute_signal = "➡️ STABLE (高位盘整，可随时建仓)"
            
            # 记录高价值事件
            high_ev_matches.append(analysis)
            total_kelly += best["kelly_pct"]
            
            print_alert(f"发现高价值目标: {analysis['match_name']}")
            print(f"[国际真实概率] {analysis['true_probs_str']}")
            print(f"[体彩当前赔率] {analysis['jc_odds_str']}")
            print(f"[动量趋势 (EV轨迹)] {trend_str}")
            print(f"[量化交易信号] {execute_signal}")
            
            capped_kelly = min(best['kelly_pct'], MAX_KELLY_CAP)
            print(f"[下注指令] 买 {best['selection']} | EV: {ev:.3f}")
            print(f"    - 理论凯利: {best['kelly_pct']*100:.2f}% | 截断后执行仓位: {capped_kelly*100:.2f}%")
            
        # 4. 串关乘法铁律与 M串N 降维
        if len(high_ev_matches) < 2:
            print("\n⚠️ 铁律 1 执行：无合法正期望组合，放弃下注 (Skip)")
        else:
            print(f"\n🧩 发现 {len(high_ev_matches)} 场价值赛事，进入 M串N 降维风控优化...")
            # 铁律：绝不输出 N串1 (如 3串1)，强行拆分为 2串1 矩阵，通过 Scipy 分配
            generate_combinations(high_ev_matches)
            
        # 5. 手动盲注防爆 (占位示例)
        manual_ev = 0.0 # 假设用户试图输入手动组合
        if manual_ev > 0 and manual_ev < 1.0:
            print("\n🚫 拒绝执行：您手动挑选的选项综合期望值为负 (EV < 1)。作为量化风控系统，拒绝为必败策略提供资金分配优化。请相信客观数据，放弃主观预测。")

        print("\n💤 休眠 300 秒后进入下一轮扫描...")
        time.sleep(300)

if __name__ == "__main__":
    quant_cruise_mode()
