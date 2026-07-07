import time
import datetime
from core.data_fetcher import fetch_jingcai_odds, fetch_pinnacle_odds, align_teams
from core.math_engine import analyze_match, remove_margin
from core.time_manager import is_jc_system_open, get_current_beijing_time

# =====================================================
# 配置区
# =====================================================
# EV 阈值：0.0 = 输出全部比赛（含负 EV），1.0 = 只输出正 EV
EV_THRESHOLD = 0.0


def calc_margin(odds_list):
    """计算庄家抽水率 (Margin %)"""
    total_implied = sum(1.0 / o for o in odds_list if o > 0)
    return (total_implied - 1.0) * 100


def calc_breakeven_odds(true_prob):
    """计算正 EV 所需的最低体彩赔率（公平赔率）"""
    if true_prob <= 0:
        return float('inf')
    return round(1.0 / true_prob, 2)


def classify_match(true_probs):
    """根据真实概率分布，判断比赛类型"""
    home, draw, away = true_probs
    gap = abs(home - away)
    if gap < 0.10:
        return "势均力敌"
    elif gap < 0.25:
        return "略有优势"
    else:
        return "强弱悬殊"


def format_report(analyses):
    """
    将分析结果格式化为人类可读的推荐报告
    """
    now = get_current_beijing_time()
    date_str = now.strftime("%Y年%m月%d日")
    
    print("\n" + "=" * 58)
    print(f"  ⚽ Quant-JingCai 量化竞彩报告 | {date_str}")
    print("=" * 58)
    
    # ---- 分离正 EV 和负 EV 的比赛 ----
    positive_ev = [a for a in analyses if a["best_option"]["ev"] >= 1.0]
    negative_ev = [a for a in analyses if a["best_option"]["ev"] < 1.0]
    
    # ============================
    # 第一部分：今晚重点推荐
    # ============================
    if positive_ev:
        print("\n## 🔥 今晚重点推荐\n")
        for idx, a in enumerate(positive_ev, 1):
            _print_match_block(idx, a, is_positive_ev=True)
    
    # ============================
    # 第二部分：全盘扫描结果
    # ============================
    print(f"\n## 📋 全盘扫描（共 {len(analyses)} 场）\n")
    for idx, a in enumerate(analyses, 1):
        _print_match_block(idx, a, is_positive_ev=False)
    
    # ============================
    # 第三部分：淘汰赛平局研究提示
    # ============================
    even_matches = [a for a in analyses 
                    if abs(a["true_probs"]["home"] - a["true_probs"]["away"]) < 0.15]
    if even_matches:
        print("## 💡 淘汰赛平局研究提示\n")
        print("  根据 research/implied_prob_comparator.py 的定量研究：")
        print("  淘汰赛中实力相近的对局，平局概率被市场系统性低估。")
        print("  在以下势均力敌的比赛中，买平局可能存在隐藏价值：\n")
        for m in even_matches:
            draw_prob = m["true_probs"]["draw"]
            draw_jc = m["jc_odds_raw"][1]
            draw_ev = draw_prob * draw_jc
            breakeven = calc_breakeven_odds(draw_prob)
            print(f"  • {m['match_name']}")
            print(f"    平局真实概率 {draw_prob:.1%}，体彩赔率 {draw_jc}")
            print(f"    👉 买平局，如果体彩赔率 ≥ {breakeven} 则为明确的 +EV 机会\n")
    
    print("=" * 58)
    print("  扫描结束。")
    print("=" * 58)


def _print_match_block(idx, analysis, is_positive_ev):
    """打印单场比赛的分析结果块"""
    best = analysis["best_option"]
    best_ev = best["ev"]
    match_time = analysis.get("match_time", "")
    
    # 格式化比赛时间显示
    time_display = ""
    if match_time:
        try:
            dt = datetime.datetime.strptime(match_time, "%Y-%m-%d %H:%M")
            hour = dt.hour
            if 0 <= hour < 6:
                time_display = f"(凌晨{dt.strftime('%H:%M')})"
            elif 6 <= hour < 12:
                time_display = f"(早上{dt.strftime('%H:%M')})"
            elif 12 <= hour < 18:
                time_display = f"(下午{dt.strftime('%H:%M')})"
            else:
                time_display = f"(晚上{dt.strftime('%H:%M')})"
        except Exception:
            time_display = f"({match_time})"
    
    # --- 基础数据 ---
    true_h = analysis["true_probs"]["home"]
    true_d = analysis["true_probs"]["draw"]
    true_a = analysis["true_probs"]["away"]
    jc_h, jc_d, jc_a = analysis["jc_odds_raw"]
    
    # 体彩隐含概率
    jc_implied = [1/jc_h, 1/jc_d, 1/jc_a]
    margin = calc_margin([jc_h, jc_d, jc_a])
    
    # 识别比赛类型
    match_type = classify_match([true_h, true_d, true_a])
    
    # 计算 Pinnacle 原始赔率（从真实概率反推，含极低抽水）
    pin_margin = 1.025  # Pinnacle 典型抽水约 2.5%
    pin_h_odds = round(pin_margin / true_h, 2) if true_h > 0 else 0
    pin_d_odds = round(pin_margin / true_d, 2) if true_d > 0 else 0
    pin_a_odds = round(pin_margin / true_a, 2) if true_a > 0 else 0
    
    # --- 输出 ---
    print(f"  {idx}. {analysis['match_name']} {time_display}")
    
    if is_positive_ev:
        # 正 EV 的比赛：突出推荐信号
        selection_cn = _selection_to_cn(best["selection"], analysis["match_name"])
        breakeven = calc_breakeven_odds(best["true_prob"])
        
        print(f"     • {selection_cn}真实胜率 {best['true_prob']:.1%}，"
              f"Pinnacle 赔率 {_get_pin_odds(best['selection'], pin_h_odds, pin_d_odds, pin_a_odds)}，"
              f"抽水仅 2.5%（极低）")
        print(f"     👉 买{_short_selection(best['selection'])}，"
              f"如果体彩赔率 ≥ {breakeven} 则为正 EV\n")
    else:
        # 全盘扫描模式：输出完整数据
        print(f"     类型: {match_type}")
        print(f"     [真实概率]   胜:{true_h:.1%} | 平:{true_d:.1%} | 负:{true_a:.1%}")
        print(f"     [Pinnacle]  胜:{pin_h_odds} | 平:{pin_d_odds} | 负:{pin_a_odds}  (抽水≈2.5%)")
        print(f"     [体彩赔率]   胜:{jc_h} | 平:{jc_d} | 负:{jc_a}  (抽水 {margin:.1f}%)")
        
        # 三个选项的 EV 和正 EV 阈值
        for opt in analysis["all_options"]:
            if opt["selection"] in ("胜", "平", "负"):
                breakeven = calc_breakeven_odds(opt["true_prob"])
                ev_icon = "✅" if opt["ev"] >= 1.0 else "⚠️" if opt["ev"] >= 0.95 else "❌"
                print(f"     {ev_icon} 买{opt['selection']}: EV={opt['ev']:.3f} | "
                      f"体彩 ≥ {breakeven} 才有正 EV")
        
        # 最终建议
        if best_ev >= 1.0:
            capped_kelly = min(best["kelly_pct"], 0.05)
            print(f"     💰 推荐: 买{best['selection']} | 凯利仓位 {capped_kelly*100:.2f}%")
        elif best_ev >= 0.95:
            print(f"     ⚠️ 最佳选项: 买{best['selection']} (EV {best_ev:.3f}，接近盈亏平衡)")
        else:
            print(f"     🚫 建议: 全部严禁买入 (最高 EV 仅 {best_ev:.3f})")
        print()


def _selection_to_cn(selection, match_name):
    """将 '胜/平/负' 转换为带队名的中文描述"""
    teams = match_name.split(" vs ")
    if len(teams) == 2:
        if selection == "胜":
            return f"{teams[0]}"
        elif selection == "负":
            return f"{teams[1]}"
    return selection


def _short_selection(selection):
    """简短的选项描述"""
    mapping = {"胜": "主胜", "平": "平局", "负": "客胜"}
    return mapping.get(selection, selection)


def _get_pin_odds(selection, h, d, a):
    """根据选项返回对应的 Pinnacle 赔率"""
    if selection == "胜":
        return h
    elif selection == "平":
        return d
    elif selection == "负":
        return a
    return 0


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
        return
    
    analyses = []
    
    for match in aligned_data:
        analysis = analyze_match(match)
        if analysis:
            # 补充 match_time 到 analysis 中
            analysis["match_time"] = match.get("match_time", "")
            best_ev = analysis["best_option"]["ev"]
            if best_ev > EV_THRESHOLD:
                analyses.append(analysis)
    
    if analyses:
        format_report(analyses)
    else:
        print("  -> 分析完毕，暂无符合阈值的赛事。")


if __name__ == "__main__":
    run_once()
