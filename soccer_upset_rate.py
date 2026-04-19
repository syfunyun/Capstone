import argparse
import pandas as pd
import os

def calculate_upset_rate(raw_data_csv, node_metrics_csv, output_csv):
    # Load raw match data and node metrics
    raw_df = pd.read_csv(raw_data_csv)
    metrics_df = pd.read_csv(node_metrics_csv)

    # Ensure required columns exist
    if 'Node' not in metrics_df.columns or 'Rank' not in metrics_df.columns:
        raise ValueError("Node metrics file must contain 'Node' and 'Rank' columns.")
    # Accept both 'Home'/'Away' and 'HomeTeam'/'AwayTeam' column names
    home_col = 'HomeTeam' if 'HomeTeam' in raw_df.columns else 'Home'
    away_col = 'AwayTeam' if 'AwayTeam' in raw_df.columns else 'Away'
    if not all(col in raw_df.columns for col in [home_col, away_col, 'FTR']):
        raise ValueError(f"Raw data file must contain '{home_col}', '{away_col}', 'FTR' columns.")

    # Build HHD ranking (higher rating = higher rank)
    hhd_ranking = metrics_df.set_index('Node')['Rank'].to_dict()

    # Track upsets and games for each team
    upset_counts = {team: 0 for team in hhd_ranking}
    game_counts = {team: 0 for team in hhd_ranking}

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
    parser = argparse.ArgumentParser(description='Calculate upset rate for each team.')
    parser.add_argument('raw_data_csv', help='Raw soccer data CSV (must have HomeTeam/AwayTeam or Home/Away, FTHG, FTAG columns)')
    parser.add_argument('node_metrics_csv', help='Node metrics CSV (must have Node and Rank columns)')
    parser.add_argument('--output', default=None, help='Output CSV file (default: auto-named from inputs)')
    args = parser.parse_args()
    # Auto-name output if not provided
    if args.output:
        output_csv = args.output
    else:
        base_raw = os.path.splitext(os.path.basename(args.raw_data_csv))[0]
        output_csv = f"upset_rates_{base_raw}.csv"
    calculate_upset_rate(args.raw_data_csv, args.node_metrics_csv, output_csv)
