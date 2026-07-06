import time
import datetime
from core.data_fetcher import fetch_jingcai_odds, fetch_pinnacle_odds, align_teams
from core.math_engine import analyze_match
from core.mn_optimizer import generate_combinations
from core.main import print_alert, TOTAL_BANKROLL
from core.time_manager import is_jc_system_open

EV_THRESHOLD = 0.0  # 临时调低到 0.0 强制获取所有比赛，以便凑够 3 场比赛演示多维玩法

def run_once():
    print("🚀 Quant-JingCai 正在执行单次扫描...")
    if not is_jc_system_open():
        print("⚠️ [警告] 当前非体彩营业时间，无法出票，指令已挂起等待系统开机。")
        # 实际部署中这里应该 return，为了测试演示流程我们继续往下走

    
    jc_matches = fetch_jingcai_odds()
    pinny_matches = fetch_pinnacle_odds() 
    
    aligned_data = align_teams(jc_matches, pinny_matches)
    
    if not aligned_data:
        print("  -> 暂时没有抓取到匹配的赛事数据。")
    
    high_ev_matches = []
    
    for match in aligned_data:
        analysis = analyze_match(match)
        if analysis:
            best_ev = analysis["best_option"]["ev"]
            if best_ev > EV_THRESHOLD:
                high_ev_matches.append(analysis)
                print_alert(analysis)
                
    if len(high_ev_matches) >= 2:
        print(f"\n🧩 发现 {len(high_ev_matches)} 场价值赛事，正在生成 M串N 容错对冲组合...")
        combos = generate_combinations(high_ev_matches)
        
        # 提取前 6 种最佳玩法
        top_6 = combos[:6]
        for i, c in enumerate(top_6):
            if isinstance(c['odds'], float):
                odds_str = f"{c['odds']:.2f}"
            else:
                odds_str = c['odds']
            print(f"   [{i+1}] {c['type']} | {c['desc']}")
            print(f"       -> 赔率指引: {odds_str} | 综合 EV: {c['ev']:.3f}\n")
                
    print("扫描结束。")

if __name__ == "__main__":
    run_once()
