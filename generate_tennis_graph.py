import pandas as pd
import networkx as nx
from collections import defaultdict
import sys
import os


def create_tennis_graph(csv_file, max_rank, year):
    df = pd.read_csv(csv_file, low_memory=False)
    # Filter by year (assumes Date column is in YYYY-MM-DD or similar format)
    df = df[df['Date'].astype(str).str.startswith(str(year))]
    # Only keep games where both players are ranked 1-max_rank
    df = df[(df['Rank_1'].between(1, max_rank)) & (df['Rank_2'].between(1, max_rank))]
    # Dictionary to store wins and matches between players
    wins = defaultdict(int)  # wins[(A, B)] = times B beat A
    total_matches = defaultdict(int)  # total_matches[(A, B)] = total matches between A and B (symmetric)

    for _, row in df.iterrows():
        p1 = row['Player_1']
        p2 = row['Player_2']
        winner = row['Winner']
        if winner == p1:
            wins[(p2, p1)] += 1  # p1 beat p2
        elif winner == p2:
            wins[(p1, p2)] += 1  # p2 beat p1
        # else: skip if winner is not one of the two (shouldn't happen)
        total_matches[(p1, p2)] += 1
        total_matches[(p2, p1)] += 1

    # Create directed graph
    G = nx.DiGraph()
    players = set(df['Player_1']).union(set(df['Player_2']))
    G.add_nodes_from(players)

    # For each unordered pair, only create one edge: from A to B, representing times B beat A
    added = set()
    for a in players:
        for b in players:
            if a == b:
                continue
            key = tuple(sorted([a, b]))
            if key in added:
                continue
            wins_b = wins[(a, b)]
            total = total_matches[(a, b)]
            if total > 0:
                weight = wins_b / total
                G.add_edge(a, b, weight=weight, wins=wins_b, total=total)
            added.add(key)

    # Display number and sizes of all components before filtering
    components = list(nx.weakly_connected_components(G))
    print(f"Number of weakly connected components before filtering: {len(components)}")
    print(f"Sizes of components: {[len(c) for c in components]}")

    # Keep only the largest weakly connected component
    if components:
        largest = max(components, key=len)
        G = G.subgraph(largest).copy()
        print(f"Saved component size: {len(largest)}")
    else:
        print("No components found. Empty graph will be saved.")
    return G


def print_graph_info(G):
    print(f"Number of players (nodes): {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    import networkx as nx
    # Weakly connected components for directed graph
    components = list(nx.weakly_connected_components(G))
    print(f"Number of weakly connected components: {len(components)}")
    print(f"Sizes of components: {[len(c) for c in components]}")
    print(f"Largest component size: {max(len(c) for c in components) if components else 0}")


def save_graph_data(G, output_file):
    import json
    data = {
        'nodes': list(G.nodes()),
        'edges': [],
        'weights': {}
    }
    for u, v, attr in G.edges(data=True):
        data['edges'].append([u, v])
        data['weights'][f"{u}->{v}"] = attr['weight']
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Graph data saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_tennis_graph.py <raw_data_csv> <max_rank> <year>")
        sys.exit(1)
    csv_file = sys.argv[1]
    max_rank = int(sys.argv[2])
    year = int(sys.argv[3])
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_file = f"TennisGraphData/{base_name}_graph_top{max_rank}_{year}.json"
    G = create_tennis_graph(csv_file, max_rank, year)
    print_graph_info(G)
    save_graph_data(G, output_file)
