import argparse
import pandas as pd
import os
import sys
from HHD import load_graph_data, hhd_ratings_unweighted

def calculate_upset_rate(raw_data_csv, graph_json_file, output_csv):
    # Load raw match data
    raw_df = pd.read_csv(raw_data_csv)
    # Load graph and compute HHD ratings
    nodes, edges, f = load_graph_data(graph_json_file)
    r = hhd_ratings_unweighted(nodes, edges, f)
    # Assign ranks: lower HHD rating = better rank (1 is best)
    sorted_nodes = sorted(nodes, key=lambda n: r[n])
    hhd_ranking = {node: rank+1 for rank, node in enumerate(sorted_nodes)}

    # Track upsets and games for each team
    upset_counts = {team: 0 for team in hhd_ranking}
    game_counts = {team: 0 for team in hhd_ranking}

    # Accept both 'Home'/'Away' and 'HomeTeam'/'AwayTeam' column names
    home_col = 'HomeTeam' if 'HomeTeam' in raw_df.columns else 'Home'
    away_col = 'AwayTeam' if 'AwayTeam' in raw_df.columns else 'Away'
    if not all(col in raw_df.columns for col in [home_col, away_col, 'FTR']):
        raise ValueError(f"Raw data file must contain '{home_col}', '{away_col}', 'FTR' columns.")

    for _, row in raw_df.iterrows():
        home = row[home_col]
        away = row[away_col]
        result = row['FTR']
        if home not in hhd_ranking or away not in hhd_ranking:
            continue  # skip teams not in ranking
        # Determine winner/loser using FTR
        if result == 'H':
            winner, loser = home, away
        elif result == 'A':
            winner, loser = away, home
        elif result == 'D':
            # Draws are not upsets
            game_counts[home] += 1
            game_counts[away] += 1
            continue
        else:
            # Unknown result, skip
            continue
        # Update game counts
        game_counts[home] += 1
        game_counts[away] += 1
        # Check for upset (lower HHD ranking is better)
        if hhd_ranking[winner] > hhd_ranking[loser]:
            # Winner is ranked worse (upset)
            upset_counts[winner] += 1
            upset_counts[loser] += 1

    # Prepare output
    results = []
    for team in hhd_ranking:
        total_upsets = upset_counts[team]
        total_games = game_counts[team]
        rate = total_upsets / total_games if total_games > 0 else 0.0
        results.append({
            'Node': team,
            'total_upsets': total_upsets,
            'total_games': total_games,
            'rate': rate
        })
    df = pd.DataFrame(results)
    df = df.sort_values('Node')
    df.to_csv(output_csv, index=False, float_format='%.6f')
    print(f"Upset rates saved to {output_csv}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python soccer_upset_rate.py <raw_data_csv> <graph_json_file>")
        sys.exit(1)
    raw_data_csv = sys.argv[1]
    graph_json_file = sys.argv[2]
    base_raw = os.path.splitext(os.path.basename(raw_data_csv))[0]
    output_csv = f"upset_rates_{base_raw}.csv"
    calculate_upset_rate(raw_data_csv, graph_json_file, output_csv)
