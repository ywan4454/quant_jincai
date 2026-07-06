import pandas as pd
import sys

def inspect_excel(filepath):
    print(f"\n--- Inspecting {filepath} ---")
    try:
        df = pd.read_excel(filepath)
        print("Columns:")
        print(list(df.columns))
        print("\nSample Data (first 3 rows):")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"Error reading file: {e}")

inspect_excel('wc2026_predictions/single_games_predictions/raw_single_odds_during_wm.xlsx')
inspect_excel('wc2026_predictions/single_games_predictions/processed_match_predictions.xlsx')
