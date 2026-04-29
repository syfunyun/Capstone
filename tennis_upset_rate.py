import sys
import pandas as pd
from collections import defaultdict
import os

def calculate_upset_rate(raw_data_csv, max_rank, year, output_csv):
    df = pd.read_csv(raw_data_csv, low_memory=False)
    # Filter by year (assumes Date column is in YYYY-MM-DD or similar format)
    df = df[df['Date'].astype(str).str.startswith(str(year))]
    # Only keep games where both players are ranked 1-max_rank
    df = df[(df['Rank_1'].between(1, max_rank)) & (df['Rank_2'].between(1, max_rank))]

    # Compute HHD ranking (lower rating = better rank)
    # For tennis, use win-loss difference as a simple rating
    players = set(df['Player_1']).union(set(df['Player_2']))
    win_counts = defaultdict(int)
    loss_counts = defaultdict(int)
    for _, row in df.iterrows():
        p1 = row['Player_1']
        p2 = row['Player_2']
        winner = row['Winner']
        if winner == p1:
            win_counts[p1] += 1
            loss_counts[p2] += 1
        elif winner == p2:
            win_counts[p2] += 1
            loss_counts[p1] += 1
    rating = {p: win_counts[p] - loss_counts[p] for p in players}
    sorted_players = sorted(players, key=lambda p: -rating[p])
    hhd_ranking = {p: rank+1 for rank, p in enumerate(sorted_players)}

    # Track upsets and games for each player
    upset_counts = {p: 0 for p in players}
    game_counts = {p: 0 for p in players}

    for _, row in df.iterrows():
        p1 = row['Player_1']
        p2 = row['Player_2']
        winner = row['Winner']
        if p1 not in hhd_ranking or p2 not in hhd_ranking:
            continue
        # Determine loser
        loser = p2 if winner == p1 else p1 if winner == p2 else None
        if loser is None:
            continue
        # Update game counts
        game_counts[p1] += 1
        game_counts[p2] += 1
        # Check for upset (winner ranked worse than loser)
        if hhd_ranking[winner] > hhd_ranking[loser]:
            upset_counts[winner] += 1
            upset_counts[loser] += 1

    results = []
    for p in players:
        total_upsets = upset_counts[p]
        total_games = game_counts[p]
        rate = total_upsets / total_games if total_games > 0 else 0.0
        results.append({
            'Node': p,
            'total_upsets': total_upsets,
            'total_games': total_games,
            'rate': rate
        })
    df_out = pd.DataFrame(results)
    df_out = df_out.sort_values('Node')
    df_out.to_csv(output_csv, index=False, float_format='%.6f')
    print(f"Upset rates saved to {output_csv}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python tennis_upset_rate.py <raw_data_csv> <max_rank> <year>")
        sys.exit(1)
    raw_data_csv = sys.argv[1]
    max_rank = int(sys.argv[2])
    year = int(sys.argv[3])
    base_raw = os.path.splitext(os.path.basename(raw_data_csv))[0]
    output_csv = f"upset_rates_{base_raw}_top{max_rank}_{year}.csv"
    calculate_upset_rate(raw_data_csv, max_rank, year, output_csv)
