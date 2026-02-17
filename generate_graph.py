import pandas as pd
import networkx as nx
from collections import defaultdict


def create_soccer_graph(csv_file):
    df = pd.read_csv(csv_file)
    
    # Dictionary to store cumulative points between teams
    # Key: (team_from, team_to), Value: points earned by team_to against team_from
    points = defaultdict(int)
    # Track total possible points for each matchup
    total_possible = defaultdict(int)
    
    for _, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        result = row['FTR']  # 'H' for home win, 'A' for away win, 'D' for draw
        
        if result == 'H':
            # Home team wins: home gets 3, away gets 0
            points[(away_team, home_team)] += 3
            points[(home_team, away_team)] += 0
        elif result == 'A':
            # Away team wins: away gets 3, home gets 0
            points[(home_team, away_team)] += 3
            points[(away_team, home_team)] += 0
        else:  # Draw
            # Both teams get 1 point
            points[(away_team, home_team)] += 1
            points[(home_team, away_team)] += 1
        
        # Each match contributes 3 possible points
        total_possible[(away_team, home_team)] += 3
        total_possible[(home_team, away_team)] += 3
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add all teams as nodes
    teams = set()
    for _, row in df.iterrows():
        teams.add(row['HomeTeam'])
        teams.add(row['AwayTeam'])
    G.add_nodes_from(teams)
    
    # Add edges with weights (proportion of points earned)
    for (team_from, team_to), pts in points.items():
        total = total_possible[(team_from, team_to)]
        if total > 0:
            weight = pts / total
            G.add_edge(team_from, team_to, weight=weight, points=pts, total=total)
    
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
        print("Usage: python generate_graph.py <csv_file> [output_json]")
        print("Example: python generate_graph.py SoccerRawData/EPLseason-2425.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Determine output file name
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Auto-generate output filename from input
        import os
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        output_file = f"SoccerGraphData/{base_name}_graph.json"
    
    # Create the graph
    G = create_soccer_graph(csv_file)
    
    # Print information
    print_graph_info(G)
    
    # Save graph data for HHD analysis
    save_graph_data(G, output_file)