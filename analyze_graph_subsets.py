import sys
import os
import networkx as nx
from itertools import combinations
from HHD import load_graph_data, hhd_ratings_unweighted, intransitive_l2_norm

def analyze_graph_subsets(json_file, max_k=None):
    nodes, edges, f = load_graph_data(json_file)
    
    # Create networkx DiGraph for easier manipulation
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # Compute original intransitivity score
    r = hhd_ratings_unweighted(nodes, edges, f)
    intransitivity = intransitive_l2_norm(edges, f, r)
    
    # Create output directory
    base_name = os.path.splitext(os.path.basename(json_file))[0]
    output_dir = f"subset_analysis_{base_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Original graph - Nodes: {G.number_of_nodes()}, Intransitivity Score: {intransitivity:.6f}\n")
    print(f"Output directory: {output_dir}\n")
    
    # If max_k is not specified, only do k=1
    if max_k is None:
        max_k = 1
    
    # Analyze removals from k=1 to max_k
    for k in range(1, max_k + 1):
        print(f"Analyzing k={k}...")
        
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
            
            # Compute intransitivity for subset
            r_subset = hhd_ratings_unweighted(nodes_subset, edges_subset, f)
            intransitivity_subset = intransitive_l2_norm(edges_subset, f, r_subset)
            
            results.append((removed_nodes, intransitivity_subset))
            count += 1
        
        if count == 0:
            print(f"  No valid subsets with edges remaining for k={k}")
            continue
        
        # Sort results by intransitivity score
        results.sort(key=lambda x: x[1])
        
        # Write results to file
        output_file = os.path.join(output_dir, f"k_{k}.txt")
        with open(output_file, 'w') as f_out:
            f_out.write(f"Analysis for k={k} (removing {k} nodes)\n")
            f_out.write(f"Total combinations analyzed: {count}\n")
            f_out.write(f"{'='*70}\n\n")
            f_out.write(f"Results (sorted by intransitivity score):\n")
            f_out.write(f"{'-'*70}\n")
            for removed_nodes, intrans in results:
                nodes_str = ", ".join(removed_nodes)
                f_out.write(f"Removed {{{nodes_str}}}: {intrans:.6f}\n")
        
        print(f"  Results saved to {output_file}")
    
    print(f"\nAnalysis complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_graph_subsets.py <json_file> [k]")
        print("Example: python analyze_graph_subsets.py SoccerGraphData/EPL_2425_graph.json 2")
        print("  k: maximum number of nodes to remove (analyzes k=1 to k)")
        print("     If not specified, defaults to k=1")
        sys.exit(1)
    
    json_file = sys.argv[1]
    max_k = None
    
    if len(sys.argv) > 2:
        try:
            max_k = int(sys.argv[2])
        except ValueError:
            print(f"Error: k must be an integer, got '{sys.argv[2]}'")
            sys.exit(1)
    
    analyze_graph_subsets(json_file, max_k)