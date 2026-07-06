import requests
import json
import os
import sys

def load_api_key():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("ODDS_API_KEY")
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        sys.exit(1)

def fetch_and_analyze():
    api_key = load_api_key()
    if not api_key:
        print("❌ 未在 config.json 中找到 odds_api_key")
        sys.exit(1)

    url = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "bookmakers": "pinnacle"
    }

    try:
        print("⏳ 正在请求 The Odds API...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API 请求失败 (可能限流或网络错误): {e}")
        sys.exit(1)

    if not data:
        print("⚠️ API 返回数据为空，没有找到相关的比赛。")
        sys.exit(0)

    draw_odds_list = []
    match_details = []
    max_draw = {"odds": 0.0, "match": ""}
    min_draw = {"odds": 999.0, "match": ""}

    for match in data:
        home_team = match.get("home_team", "Unknown")
        away_team = match.get("away_team", "Unknown")
        match_name = f"{home_team} vs {away_team}"
        
        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            continue
            
        # 我们已经指定了 bookmakers=pinnacle，所以如果有数据，必定是 pinnacle
        pinnacle_data = bookmakers[0]
        markets = pinnacle_data.get("markets", [])
        
        if not markets:
            continue
            
        h2h_market = markets[0] # markets=h2h
        outcomes = h2h_market.get("outcomes", [])
        
        h_odds, d_odds, a_odds = 0.0, 0.0, 0.0
        for outcome in outcomes:
            name = outcome.get("name")
            price = outcome.get("price")
            if name == "Draw":
                d_odds = price
            elif name == home_team:
                h_odds = price
            elif name == away_team:
                a_odds = price

        if d_odds > 0:
            draw_odds_list.append(d_odds)
            match_details.append(f"{match_name} | 胜: {h_odds:.2f} | 平: {d_odds:.2f} | 负: {a_odds:.2f}")
            
            if d_odds > max_draw["odds"]:
                max_draw = {"odds": d_odds, "match": match_name}
            if d_odds < min_draw["odds"]:
                min_draw = {"odds": d_odds, "match": match_name}

    if not draw_odds_list:
        print("⚠️ 没有解析到任何合法的平局赔率。")
        sys.exit(0)

    avg_draw_odds = sum(draw_odds_list) / len(draw_odds_list)

    # 打印可视化输出
    print("\n=========================================================")
    print("📊 2026 世界杯比赛 (Pinnacle 平博) 平局赔率复盘报告")
    print("=========================================================")
    print("[综合统计]")
    print(f"- 统计场次：{len(draw_odds_list)} 场")
    print(f"- 算术平均平局赔率：{avg_draw_odds:.2f}")
    print(f"- 最高平局赔率：{max_draw['odds']:.2f} (比赛: {max_draw['match']})")
    print(f"- 最低平局赔率：{min_draw['odds']:.2f} (比赛: {min_draw['match']})")
    print("---------------------------------------------------------")
    print("[逐场明细清单]")
    for i, detail in enumerate(match_details, 1):
        print(f"{i}. {detail}")
    print("=========================================================\n")

if __name__ == "__main__":
    fetch_and_analyze()
