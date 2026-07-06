import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore')

def analyze():
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wc2026_predictions/single_games_predictions/processed_match_predictions.xlsx')
    df = pd.read_excel(file_path)
    
    # Filter for draw probabilities
    df_draws = df[df['Ausgang'] == 'Unentschieden'].copy()
    
    # Parse date correctly (format in excel might be DD.MM.YYYY)
    df_draws['Datum_parsed'] = pd.to_datetime(df_draws['Datum'], format='%d.%m.%Y', errors='coerce')
    
    # For 2026 World Cup, group stage finishes around June 27th.
    # We classify matches up to 2026-06-27 as Group Stage, and from 2026-06-28 as Knockout.
    df_draws['Stage'] = df_draws['Datum_parsed'].apply(
        lambda x: 'Group Stage' if pd.notnull(x) and x <= pd.Timestamp('2026-06-27') else 'Knockout Stage'
    )
    
    # Sort by date
    df_draws = df_draws.sort_values('Datum_parsed')
    
    # 1. Summary Statistics
    summary = df_draws.groupby('Stage').agg(
        Total_Matches=('Spiel_ID', 'count'),
        Avg_Raw_Implied_Prob=('Wahrscheinlichkeit', 'mean'),
        Avg_Shin_Prob=('Wahrscheinlichkeit_Shin', 'mean')
    ).reset_index()
    
    summary['Avg_Raw_Implied_Prob'] = summary['Avg_Raw_Implied_Prob'].apply(lambda x: f"{x:.2%}")
    summary['Avg_Shin_Prob'] = summary['Avg_Shin_Prob'].apply(lambda x: f"{x:.2%}")
    
    print("=== Draw Probability Change (Group vs Knockout) ===")
    print(summary.to_string(index=False))
    
    # 2. Time-series data
    daily_trend = df_draws.groupby('Datum_parsed').agg(
        Avg_Shin_Prob=('Wahrscheinlichkeit_Shin', 'mean'),
        Matches=('Spiel_ID', 'count')
    ).reset_index()
    
    print("\n=== Daily Trend of Shin Draw Probability ===")
    for _, row in daily_trend.iterrows():
        date_str = row['Datum_parsed'].strftime('%Y-%m-%d')
        prob_str = f"{row['Avg_Shin_Prob']:.2%}"
        print(f"{date_str}: {prob_str} ({int(row['Matches'])} matches)")

if __name__ == '__main__':
    analyze()
