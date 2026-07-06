import csv
import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get('ODDS_API_KEY', '')
if not API_KEY and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')):
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json'), 'r') as f:
            config = json.load(f)
            API_KEY = config.get('ODDS_API_KEY', '')
    except Exception as e:
        print(f"Could not read config.json: {e}")

def fetch_or_mock_data():
    data = []
    if API_KEY:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds"
            params = {
                "apiKey": API_KEY,
                "regions": "eu",
                "markets": "h2h",
                "bookmakers": "pinnacle"
            }
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                events = resp.json()
                for event in events:
                    home = event.get('home_team')
                    away = event.get('away_team')
                    match_name = f"{home} vs {away}"
                    commence_time = event.get('commence_time')
                    
                    pinnacle_draw_odds = None
                    for bookmaker in event.get('bookmakers', []):
                        if bookmaker['key'] == 'pinnacle':
                            for market in bookmaker.get('markets', []):
                                if market['key'] == 'h2h':
                                    for outcome in market.get('outcomes', []):
                                        if outcome['name'] == 'Draw':
                                            pinnacle_draw_odds = outcome['price']
                    
                    if pinnacle_draw_odds is not None:
                        data.append([match_name, commence_time, pinnacle_draw_odds])
                if data:
                    return data
            else:
                print(f"API request failed with status: {resp.status_code}")
        except Exception as e:
            print(f"Failed to fetch from API: {e}")
    
    print("Using mock data as API key is not provided or API call failed...")
    # Mock data for World Cup 2026 Group Stage
    mock_events = [
        ["USA vs Wales", "2026-06-12T19:00:00Z", 3.20],
        ["Argentina vs Saudi Arabia", "2026-06-13T10:00:00Z", 6.50],
        ["France vs Australia", "2026-06-14T19:00:00Z", 5.00],
        ["Spain vs Costa Rica", "2026-06-15T16:00:00Z", 4.80],
        ["Germany vs Japan", "2026-06-16T13:00:00Z", 3.80],
        ["Brazil vs Serbia", "2026-06-17T19:00:00Z", 4.10],
        ["Portugal vs Ghana", "2026-06-18T16:00:00Z", 3.50],
        ["England vs Iran", "2026-06-19T13:00:00Z", 4.00],
    ]
    return mock_events

def main():
    events = fetch_or_mock_data()
    
    # Task 1: Format and save to CSV
    # Including Task 2: Implied Probability in the same CSV
    csv_file = '2026_wc_group_draw_odds.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Adding header
        writer.writerow(["比赛名称 (Match Name)", "开球时间 (Kickoff Time)", "平博平局赔率 (Pinnacle Draw Odds)", "隐含平局率 (Implied Probability)"])
        
        for event in events:
            match_name, kickoff_time, odds = event
            
            # Task 2: Calculate Implied Probability
            implied_prob = (1 / odds) if odds else None
            implied_prob_str = f"{implied_prob:.2%}" if implied_prob else "N/A"
            
            # Write row
            writer.writerow([match_name, kickoff_time, odds, implied_prob_str])
            
    print(f"Data successfully written to {os.path.abspath(csv_file)}")

if __name__ == "__main__":
    main()
