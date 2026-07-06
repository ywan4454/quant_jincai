import os
import pandas as pd
import glob
import numpy as np
import warnings

warnings.filterwarnings('ignore')

def analyze_pinnacle_odds():
    print("=== jokecamp/FootballData: Pinnacle Draw Odds Backtesting ===")
    # Find all CSV files in FootballData that might contain PSD
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FootballData/**/*.csv")
    csv_files = glob.glob(path, recursive=True)
    
    psd_matches = []
    
    for file in csv_files:
        try:
            # Check if columns exist
            df = pd.read_csv(file, on_bad_lines='skip', low_memory=False)
            if 'PSD' in df.columns and 'FTR' in df.columns:
                df_filtered = df[['FTR', 'PSD']].dropna()
                # Ensure PSD is numeric
                df_filtered['PSD'] = pd.to_numeric(df_filtered['PSD'], errors='coerce')
                df_filtered = df_filtered.dropna()
                psd_matches.append(df_filtered)
        except Exception as e:
            pass
            
    if psd_matches:
        all_matches = pd.concat(psd_matches, ignore_index=True)
        # Calculate Implied Probability vs Actual Result
        all_matches['Implied_Draw_Prob'] = 1 / all_matches['PSD']
        all_matches['Is_Draw'] = (all_matches['FTR'] == 'D').astype(int)
        
        # Group by Implied Probability buckets
        bins = [0, 0.2, 0.25, 0.3, 0.35, 0.4, 1.0]
        labels = ['<20%', '20-25%', '25-30%', '30-35%', '35-40%', '>40%']
        all_matches['Prob_Bucket'] = pd.cut(all_matches['Implied_Draw_Prob'], bins=bins, labels=labels)
        
        summary = all_matches.groupby('Prob_Bucket').agg(
            Total_Matches=('Is_Draw', 'count'),
            Actual_Draws=('Is_Draw', 'sum')
        ).reset_index()
        summary['Actual_Draw_Rate'] = (summary['Actual_Draws'] / summary['Total_Matches']).apply(lambda x: f"{x:.2%}")
        
        print(f"Total analyzed matches with Pinnacle Draw Odds: {len(all_matches)}")
        print("\nBacktesting Results (Implied vs Actual Draw Rate):")
        print(summary.to_string(index=False))
    else:
        print("No matches with PSD found.")

def analyze_worldcup_baseline():
    print("\n=== jfjelstul/worldcup: World Cup Draw Distribution Baseline ===")
    matches_file = "worldcup/data-csv/matches.csv"
    if not os.path.exists(matches_file):
        print(f"File {matches_file} not found.")
        return
        
    df = pd.read_csv(matches_file)
    
    # Use historical appearances as proxy for team strength (Pot 1 vs Pot 4)
    team_counts = pd.concat([df['home_team_name'], df['away_team_name']]).value_counts()
    
    pot1_teams = team_counts.head(8).index.tolist()
    # Bottom 50% appearances as Pot 4
    pot4_teams = team_counts.tail(int(len(team_counts)*0.5)).index.tolist()
    
    def is_pot1_vs_pot4(row):
        h, a = row['home_team_name'], row['away_team_name']
        return (h in pot1_teams and a in pot4_teams) or (a in pot1_teams and h in pot4_teams)
        
    def is_pot1_vs_pot1(row):
        h, a = row['home_team_name'], row['away_team_name']
        return h in pot1_teams and a in pot1_teams

    df['Pot1_vs_Pot4'] = df.apply(is_pot1_vs_pot4, axis=1)
    df['Pot1_vs_Pot1'] = df.apply(is_pot1_vs_pot1, axis=1)
    
    pot1_pot4_matches = df[df['Pot1_vs_Pot4']]
    pot1_pot1_matches = df[df['Pot1_vs_Pot1']]
    all_group_matches = df[df['stage_name'] == 'group stage']
    
    print(f"Pot 1 Proxy Teams (Top 8 historically): {', '.join(pot1_teams)}")
    print(f"Total World Cup Matches in Dataset: {len(df)}")
    print(f"Overall Draw Rate: {df['draw'].mean():.2%}")
    print(f"Group Stage Draw Rate: {all_group_matches['draw'].mean():.2%}")
    if len(pot1_pot4_matches) > 0:
        print(f"Pot 1 vs Pot 4 Proxy Draw Rate ({len(pot1_pot4_matches)} matches): {pot1_pot4_matches['draw'].mean():.2%}")
    if len(pot1_pot1_matches) > 0:
        print(f"Pot 1 vs Pot 1 Proxy Draw Rate ({len(pot1_pot1_matches)} matches): {pot1_pot1_matches['draw'].mean():.2%}")

if __name__ == "__main__":
    analyze_pinnacle_odds()
    analyze_worldcup_baseline()
