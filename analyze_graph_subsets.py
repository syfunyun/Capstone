import sys
import os
import networkx as nx
from itertools import combinations
import pandas as pd
from HHD import load_graph_data, hhd_ratings_unweighted, intransitive_l2_norm, transitive_l2_norm, total_l2_norm, hhd_decomposition


def export_hhd_rankings(nodes, edges, f, output_file):
    """
    Export HHD rankings for given nodes and edges to CSV
    """
    if len(edges) == 0:
        return
    
    r = hhd_ratings_unweighted(nodes, edges, f)
    
    # Compute vorticities
    vorticities = {node: 0.0 for node in nodes}
    for (i, j) in edges:
        curl_ij = f[(i, j)] - (r[i] - r[j])
        vorticities[i] += curl_ij
        vorticities[j] -= curl_ij
    
    # Create ranking data
    ranking_data = []
    for node in nodes:
        ranking_data.append({
            'Node': node,
            'HHD_Rating': r[node],
            'Vorticity': vorticities[node]
        })
    
    # Sort by HHD_Rating (descending)
    ranking_data.sort(key=lambda x: x['HHD_Rating'], reverse=True)
    
    # Add rank column
    for rank, item in enumerate(ranking_data, 1):
        item['Rank'] = rank
    
    # Create DataFrame and reorder columns
    df = pd.DataFrame(ranking_data)
    df = df[['Rank', 'Node', 'HHD_Rating', 'Vorticity']]
    
    # Save to CSV
    df.to_csv(output_file, index=False, float_format='%.6f')

def analyze_graph_subsets(json_file, max_k):
    nodes, edges, f = load_graph_data(json_file)
    
    # Create networkx DiGraph for easier manipulation
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # Compute original intransitivity score
    r = hhd_ratings_unweighted(nodes, edges, f)
    intransitivity = intransitive_l2_norm(edges, f, r)
    transitivity = transitive_l2_norm(edges, f, r)
    total = total_l2_norm(edges, f, r)
    
    print(f"Original graph - Nodes: {G.number_of_nodes()}, Intransitivity Score: {intransitivity:.6f}, Percentage: {100*(intransitivity / total if total > 0 else 0):.2f}%\n")
    
    all_results = []
    
    base_name = os.path.splitext(os.path.basename(json_file))[0]
    
    # Analyze from k=0 to max_k
    for k in range(max_k + 1):
        print(f"Analyzing k={k}...")
        
        if k == 0:
            # Baseline: no nodes removed
            percentage = 100 * (intransitivity / total) if total > 0 else 0
            all_results.append({
                'k': k,
                'Removed_Nodes': '{}',
                'Intransitivity': intransitivity,
                'Transitivity': transitivity,
                'Total': total,
                'Intransitivity_Percentage': percentage,
                'Nodes_Remaining': len(nodes),
                'Edges_Remaining': len(edges)
            })
            
            # No rankings export
            
            print(f"  Baseline: 1 combination")
            continue
        
        results = []
        count = 0
        
        for removed_nodes in combinations(nodes, k):
            G_subset = G.copy()
            for node in removed_nodes:
                G_subset.remove_node(node)
            
            nodes_subset = list(G_subset.nodes())
            edges_subset = list(G_subset.edges())
            
            if len(edges_subset) == 0:
                continue
            
            # Compute metrics for subset
            r_subset = hhd_ratings_unweighted(nodes_subset, edges_subset, f)
            intransitivity_subset = intransitive_l2_norm(edges_subset, f, r_subset)
            transitivity_subset = transitive_l2_norm(edges_subset, f, r_subset)
            total_subset = total_l2_norm(edges_subset, f, r_subset)
            percentage_subset = 100 * (intransitivity_subset / total_subset) if total_subset > 0 else 0
            
            removed_str = '{' + ', '.join(sorted(removed_nodes)) + '}'
            results.append({
                'k': k,
                'Removed_Nodes': removed_str,
                'Intransitivity': intransitivity_subset,
                'Transitivity': transitivity_subset,
                'Total': total_subset,
                'Intransitivity_Percentage': percentage_subset,
                'Nodes_Remaining': len(nodes_subset),
                'Edges_Remaining': len(edges_subset)
            })
            
            # No rankings export for subsets
            
            count += 1
        
        if count == 0:
            print(f"  No valid subsets with edges remaining for k={k}")
            continue
        
        all_results.extend(results)
        print(f"  Added {count} combinations")
    
    if not all_results:
        print("No results to save")
        return
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_results)
    
    # Sort by k, then by Intransitivity_Percentage
    df = df.sort_values(['k', 'Intransitivity_Percentage'])
    
    output_file = f"subset_analysis_{base_name}_k0_to_{max_k}.csv"
    df.to_csv(output_file, index=False, float_format='%.6f')
    
    print(f"\nResults saved to {output_file} ({len(all_results)} total combinations)")
    
    print(f"\nAnalysis complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze_graph_subsets.py <json_file> <max_k>")
        print("Example: python analyze_graph_subsets.py SoccerGraphData/EPL_2425_graph.json 2")
        print("  json_file: path to the graph JSON file")
        print("  max_k: maximum number of nodes to remove (analyzes k=0 to max_k)")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        max_k = int(sys.argv[2])
        if max_k < 0:
            raise ValueError("max_k must be non-negative")
    except ValueError:
        print(f"Error: max_k must be a non-negative integer, got '{sys.argv[2]}'")
        sys.exit(1)
    
    analyze_graph_subsets(json_file, max_k)