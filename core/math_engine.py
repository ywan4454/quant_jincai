def remove_margin(odds_list):
    """
    通过基础的比例衰减法去除博彩公司抽水 (Margin)
    返回真实的概率列表
    """
    implied_probs = [1.0 / o for o in odds_list]
    margin = sum(implied_probs)
    true_probs = [p / margin for p in implied_probs]
    return true_probs

def calculate_ev(true_prob, jc_odds):
    """计算数学期望 (Expected Value)"""
    return true_prob * jc_odds

def kelly_criterion(true_prob, jc_odds, fraction=0.25):
    """计算凯利建议仓位"""
    b = jc_odds - 1.0
    if b <= 0: return 0.0
    q = 1.0 - true_prob
    f_star = (b * true_prob - q) / b
    if f_star > 0:
        return f_star * fraction
    return 0.0

def analyze_match(aligned_match):
    """
    量化核心：计算单场比赛多玩法（胜平负、总进球、半全场）的数学期望。
    """
    # 1. 胜平负 (SPF - 1X2)
    pin_home = aligned_match.get("pin_home_name", "")
    pin_away = aligned_match.get("pin_away_name", "")
    
    pin_odds = aligned_match.get("pin_odds", {})
    pin_odds_list = [
        pin_odds.get(pin_home, 0),
        pin_odds.get("Draw", 0),
        pin_odds.get(pin_away, 0)
    ]
    
    # 模拟数据填充：在 The Odds API 没有提供确切的总进球和半全场分布时，
    # 我们可以通过泊松分布或历史权重矩阵，将 1X2 的真实概率映射到其他盘口。
    # 这里为了系统闭环，如果抓取到了 ZJQ 或 BQC 数据，我们会用占位的 true_prob 来结算 EV。
    
    jc_odds_dict = aligned_match.get("jc_odds", {})
    if "had" in jc_odds_dict:
        jc_odds_list = [jc_odds_dict["had"]["h"], jc_odds_dict["had"]["d"], jc_odds_dict["had"]["a"]]
    elif "h" in jc_odds_dict: # 兼容老结构
        jc_odds_list = [jc_odds_dict.get("h", 0), jc_odds_dict.get("d", 0), jc_odds_dict.get("a", 0)]
    else:
        jc_odds_list = [0, 0, 0]
        
    if 0 in pin_odds_list or 0 in jc_odds_list:
        return None
        
    true_probs = remove_margin(pin_odds_list)
    labels = ["胜", "平", "负"]
    results = []
    
    # 1. 主盘口 (1X2)
    for i in range(3):
        true_p = true_probs[i]
        jc_o = jc_odds_list[i]
        if jc_o > 0:
            ev = calculate_ev(true_p, jc_o)
            kelly_pct = kelly_criterion(true_p, jc_o, fraction=0.25)
            results.append({
                "selection": labels[i],
                "true_prob": true_p,
                "jc_odds": jc_o,
                "ev": ev,
                "kelly_pct": kelly_pct
            })
            
    # 2. 让球盘口 (RQSPF)
    hhad = jc_odds_dict.get("hhad")
    if hhad:
        # 极简泊松映射：让球会使得主胜概率降低，客胜概率升高。
        # 此处使用简单的线性衰减作为演示模型，实盘需要引入严格的积分函数。
        handicap = hhad["handicap"]
        rq_true_h = true_probs[0] * 0.6 if handicap < 0 else true_probs[0] * 1.4
        rq_true_a = true_probs[2] * 1.4 if handicap < 0 else true_probs[2] * 0.6
        rq_true_d = 1.0 - rq_true_h - rq_true_a
        
        rq_probs = [rq_true_h, rq_true_d, rq_true_a]
        rq_jc = [hhad["h"], hhad["d"], hhad["a"]]
        rq_labels = [f"让球({handicap})胜", f"让球({handicap})平", f"让球({handicap})负"]
        
        for i in range(3):
            if rq_jc[i] > 0 and rq_probs[i] > 0:
                ev = calculate_ev(rq_probs[i], rq_jc[i])
                kelly_pct = kelly_criterion(rq_probs[i], rq_jc[i], fraction=0.25)
                results.append({
                    "selection": rq_labels[i],
                    "true_prob": rq_probs[i],
                    "jc_odds": rq_jc[i],
                    "ev": ev,
                    "kelly_pct": kelly_pct
                })
                
    # 3. 总进球 (ZJQ)
    zjq = jc_odds_dict.get("zjq")
    if zjq:
        # 演示用：假定 0球 和 1球 的理论概率分布，这应该从 totals 接口获取并建模
        zjq_mock_probs = {"0": 0.15, "1": 0.20, "2": 0.25, "3": 0.20, "4": 0.10, "5": 0.05, "6": 0.03, "7+": 0.02}
        for goals, odds_val in zjq.items():
            tp = zjq_mock_probs.get(goals, 0.01)
            ev = calculate_ev(tp, odds_val)
            kelly_pct = kelly_criterion(tp, odds_val, fraction=0.25)
            results.append({
                "selection": f"总进球:{goals}",
                "true_prob": tp,
                "jc_odds": odds_val,
                "ev": ev,
                "kelly_pct": kelly_pct
            })
            
    # 4. 半全场 (BQC)
    bqc = jc_odds_dict.get("bqc")
    if bqc:
        # 演示用：胜胜 的概率约等于 胜 的平方（简单贝叶斯）
        for bqc_type, odds_val in bqc.items():
            tp = true_probs[0] * true_probs[0] if "胜胜" in bqc_type else 0.08
            ev = calculate_ev(tp, odds_val)
            kelly_pct = kelly_criterion(tp, odds_val, fraction=0.25)
            results.append({
                "selection": f"半全场:{bqc_type}",
                "true_prob": tp,
                "jc_odds": odds_val,
                "ev": ev,
                "kelly_pct": kelly_pct
            })
            
    best_option = max(results, key=lambda x: x["ev"])
    
    # 构建兼容 Dutching 的返回值格式
    return {
        "match_name": aligned_match["match_name"],
        "true_probs_str": f"胜:{true_probs[0]:.1%} | 平:{true_probs[1]:.1%} | 负:{true_probs[2]:.1%}",
        "jc_odds_str": f"胜:{jc_odds_list[0]} | 平:{jc_odds_list[1]} | 负:{jc_odds_list[2]}",
        "best_option": best_option,
        "all_options": results,
        "jc_odds_raw": [jc_odds_list[0], jc_odds_list[1], jc_odds_list[2]],
        "true_probs": {"home": true_probs[0], "draw": true_probs[1], "away": true_probs[2]}
    }
