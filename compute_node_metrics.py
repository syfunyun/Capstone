import sys
import os
import pandas as pd
import networkx as nx
from HHD import load_graph_data, hhd_ratings_unweighted


def compute_intransitivity_centrality(subset_csv):
    
    subset_df = pd.read_csv(subset_csv)
    
    # Get baseline (k=0) intransitivity percentage
    baseline_row = subset_df[subset_df['k'] == 0]
    if len(baseline_row) == 0:
        print("Warning: No baseline (k=0) found in subset analysis")
        return {}
    
    baseline_percentage = baseline_row.iloc[0]['Intransitivity_Percentage']
    print(f"Baseline intransitivity: {baseline_percentage:.3f}%")
    
    # Get all k values > 0
    k_values = sorted(subset_df[subset_df['k'] > 0]['k'].unique())
    print(f"Computing centrality for k values: {k_values}")
    
    # Initialize results dict
    centrality_results = {}
    
    # Get all unique nodes from the dataset
    all_nodes = set()
    for _, row in subset_df.iterrows():
        if row['k'] > 0 and pd.notna(row['Removed_Nodes']):
            # Parse the removed nodes (format: {Node1,Node2,...} or {Node1})
            removed_str = row['Removed_Nodes'].strip('{}')
            if removed_str:
                nodes = [n.strip() for n in removed_str.split(',')]
                all_nodes.update(nodes)
    
    # Initialize centrality dict for each node
    for node in all_nodes:
        centrality_results[node] = {}
    
    # Compute k=1 centrality (traditional)
    k1_df = subset_df[subset_df['k'] == 1]
    if len(k1_df) > 0:
        for _, row in k1_df.iterrows():
            removed_str = row['Removed_Nodes'].strip('{}').strip()
            if removed_str:
                centrality = baseline_percentage - row['Intransitivity_Percentage']
                centrality_results[removed_str]['k1_centrality'] = centrality
    
    # Removed avg_impact_kN measures for k > 1
    
    # Convert to the expected format for backward compatibility
    # Return k1_centrality as the main centrality value
    final_centrality = {}
    for node, measures in centrality_results.items():
        if 'k1_centrality' in measures:
            final_centrality[node] = measures['k1_centrality']
        else:
            final_centrality[node] = 0.0
    
    print(f"Computed comprehensive centrality for {len(final_centrality)} nodes")
    return final_centrality, centrality_results


def compute_additional_centralities(nodes, edges, f):
    
    # Create NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    # Add weighted edges
    for i, j in edges:
        # Use absolute value of weight for centrality calculations
        # (since some centralities work better with positive weights)
        weight = abs(f[(i, j)])
        G.add_edge(i, j, weight=weight)
    
    centralities = {}
    
    try:
        # Weighted degree centrality (manual calculation: sum of absolute edge weights)
        weighted_degrees = {}
        for node in nodes:
            degree_sum = 0
            for neighbor in G.neighbors(node):
                degree_sum += abs(f.get((node, neighbor), f.get((neighbor, node), 0)))
            weighted_degrees[node] = degree_sum
        
        # Normalize by maximum weighted degree
        max_weighted_degree = max(weighted_degrees.values()) if weighted_degrees else 1
        centralities['Weighted_Degree'] = {node: val/max_weighted_degree for node, val in weighted_degrees.items()}
        print(f"Weighted degree centrality computed for {len(centralities['Weighted_Degree'])} nodes")
    except Exception as e:
        print(f"Warning: Could not compute weighted degree centrality: {e}")
        centralities['Weighted_Degree'] = {node: 0.0 for node in nodes}
    
    # Removed Betweenness centrality calculation
    
    # Removed Closeness centrality calculation
    
    try:
        # Eigenvector centrality
        eigenvector_cent = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        centralities['Eigenvector'] = eigenvector_cent
        print(f"Eigenvector centrality computed for {len(centralities['Eigenvector'])} nodes")
    except Exception as e:
        print(f"Warning: Could not compute eigenvector centrality: {e}")
        centralities['Eigenvector'] = {node: 0.0 for node in nodes}
    
    try:
        # PageRank centrality (more robust than Katz for this type of graph)
        pagerank_cent = nx.pagerank(G, weight='weight', alpha=0.85, max_iter=1000)
        centralities['PageRank'] = pagerank_cent
        print(f"PageRank centrality computed for {len(centralities['PageRank'])} nodes")
    except Exception as e:
        print(f"Warning: Could not compute PageRank centrality: {e}")
        centralities['PageRank'] = {node: 0.0 for node in nodes}
    
    return centralities


def extract_node_metrics(json_file, subset_csv_file=None):
    
    nodes, edges, f = load_graph_data(json_file)
    
    if len(edges) == 0:
        print("Error: Graph has no edges")
        # Removed Weighted_Degree centrality calculation
    
    # Compute HHD ratings
    r = hhd_ratings_unweighted(nodes, edges, f)

    # Create ranking data with ranks
    ranking_data = []
    rankings = {}  # node -> rank mapping
    for node in nodes:
        ranking_data.append({
            'Node': node,
            'HHD_Rating': r[node]
        })
    # Sort by HHD_Rating (ascending)
    ranking_data.sort(key=lambda x: x['HHD_Rating'])
    # Add rank column
    for rank, item in enumerate(ranking_data, 1):
        item['Rank'] = rank
        rankings[item['Node']] = rank
    # Create DataFrame
    df = pd.DataFrame(ranking_data)
    # Merge in upset rates if provided
    if hasattr(extract_node_metrics, 'upset_csv_file') and extract_node_metrics.upset_csv_file:
        upset_df = pd.read_csv(extract_node_metrics.upset_csv_file)
        if 'Node' in upset_df.columns and 'rate' in upset_df.columns:
            df = df.merge(upset_df[['Node', 'rate']], on='Node', how='left')
            df = df.rename(columns={'rate': 'Upset_rate'})
            print(f"Merged upset rates for {df['Upset_rate'].count()} nodes")
        else:
            print("Warning: Upset rate CSV must have 'Node' and 'rate' columns. Skipping upset rate merge.")
    
    # Compute intransitivity centrality if subset CSV provided
    if subset_csv_file:
        centrality_result = compute_intransitivity_centrality(subset_csv_file)
        if isinstance(centrality_result, tuple):
            centrality_data, detailed_centrality = centrality_result
        else:
            # Backward compatibility
            centrality_data = centrality_result
            detailed_centrality = {}
        
        if centrality_data:
            df['Intransitivity_Centrality'] = df['Node'].map(centrality_data)
            print(f"Intransitivity centrality computed for {len(centrality_data)} nodes")
            
            # Removed adding detailed avg_impact_kN centrality measures to DataFrame
    
    # (Removed) Compute additional graph centralities: Eigenvector and PageRank
    # Only output Node, Rank, HHD_Rating, Intransitivity_Centrality, Upset_rate
    columns = ['Node', 'Rank', 'HHD_Rating']
    if 'Intransitivity_Centrality' in df.columns:
        columns.append('Intransitivity_Centrality')
    if 'Upset_rate' in df.columns:
        columns.append('Upset_rate')
    df = df[columns]
    
    # Save to CSV (always overwrite with latest results)
    base_name = os.path.splitext(os.path.basename(json_file))[0]
    output_file = f"node_metrics_{base_name}.csv"
    df.to_csv(output_file, index=False, float_format='%.6f')
    print(f"Wrote latest metrics to {output_file}")
    print(f"Total nodes: {len(df)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compute_node_metrics.py <graph_json_file> <subset_analysis_csv> [upset_rate_csv]")
        sys.exit(1)

    json_file = sys.argv[1]
    subset_csv = sys.argv[2]
    upset_csv = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)

    if upset_csv and not os.path.exists(upset_csv):
        print(f"Error: File '{upset_csv}' not found")
        sys.exit(1)

    if subset_csv and not os.path.exists(subset_csv):
        print(f"Error: File '{subset_csv}' not found")
        sys.exit(1)

    # If upset_csv is missing or empty, skip upset rate merge
    if upset_csv and os.path.exists(upset_csv):
        extract_node_metrics.upset_csv_file = upset_csv
    else:
        extract_node_metrics.upset_csv_file = None

    extract_node_metrics(json_file, subset_csv)
