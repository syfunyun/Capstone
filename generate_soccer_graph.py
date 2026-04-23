import pandas as pd
import networkx as nx
from collections import defaultdict


def create_soccer_graph(csv_file):
    df = pd.read_csv(csv_file)
    
    # Dictionary to store points earned by each team against each other
    points = defaultdict(int)  # points[(A, B)] = points B earned vs A
    total_points = defaultdict(int)  # total_points[(A, B)] = total points in A vs B (symmetric)

    for _, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        result = row['FTR']

        if result == 'H':
            # Home win: home gets 3, away gets 0
            points[(away, home)] += 3  # points home earned vs away
            # points[(home, away)] += 0  # not needed, default is 0
            total_points[(home, away)] += 3
            total_points[(away, home)] += 3
        elif result == 'A':
            # Away win: away gets 3, home gets 0
            points[(home, away)] += 3  # points away earned vs home
            # points[(away, home)] += 0  # not needed, default is 0
            total_points[(home, away)] += 3
            total_points[(away, home)] += 3
        else:  # Draw
            # Both get 1 point, but only 2 points total
            points[(away, home)] += 1
            points[(home, away)] += 1
            total_points[(home, away)] += 2
            total_points[(away, home)] += 2

    # Create directed graph
    G = nx.DiGraph()

    # Add all teams as nodes
    teams = set(df['HomeTeam']).union(set(df['AwayTeam']))
    G.add_nodes_from(teams)

    # For each unordered pair, only create one edge: from A to B, representing points B earned vs A
    added = set()
    for team_a in teams:
        for team_b in teams:
            if team_a == team_b:
                continue
            key = tuple(sorted([team_a, team_b]))
            if key in added:
                continue
            # Edge from A to B: points B earned vs A
            pts_b = points[(team_a, team_b)]
            total = total_points[(team_a, team_b)]
            if total > 0:
                weight = pts_b / total
                G.add_edge(team_a, team_b, weight=weight, points=pts_b, total=total)
            added.add(key)

    return G


def print_graph_info(G):
    print(f"Number of teams (nodes): {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")


def save_graph_data(G, output_file):
    import json
    
    # Prepare data structure
    data = {
        'nodes': list(G.nodes()),
        'edges': [],
        'weights': {}
    }
    
    for u, v, attr in G.edges(data=True):
        data['edges'].append([u, v])
        data['weights'][f"{u}->{v}"] = attr['weight']
    
    # Save to JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Graph data saved to {output_file}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_soccer_graph.py <raw_data_csv>")
        sys.exit(1)
    csv_file = sys.argv[1]
    import os
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_file = f"SoccerGraphData/{base_name}_graph.json"
    # Create the graph
    G = create_soccer_graph(csv_file)
    # Print information
    print_graph_info(G)
    # Save graph data for HHD analysis
    save_graph_data(G, output_file)