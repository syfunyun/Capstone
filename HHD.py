import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
import json
import sys


def hhd_ratings_unweighted(nodes, edges, f):
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}
    n = len(nodes)
    
    L = lil_matrix((n, n))
    b = np.zeros(n)

    for (i, j) in edges:
        i_idx = node_to_idx[i]
        j_idx = node_to_idx[j]
        
        # Laplacian
        L[i_idx, i_idx] += 1
        L[j_idx, j_idx] += 1
        L[i_idx, j_idx] -= 1
        L[j_idx, i_idx] -= 1

        # Divergence
        fij = f[(i, j)]
        b[i_idx] += fij
        b[j_idx] -= fij

    # Fix gauge: r[n-1] = 0
    L = L.tocsr()
    L_reduced = L[:-1, :-1]
    b_reduced = b[:-1]

    r_reduced = spsolve(L_reduced, b_reduced)

    r_array = np.zeros(n)
    r_array[:-1] = r_reduced
    r_array[-1] = 0.0

    # Center
    r_array -= r_array.mean()

    r = {node: r_array[node_to_idx[node]] for node in nodes}
    
    return r


def hhd_decomposition(edges, f, r):
    grad = {}
    curl = {}

    for (i, j) in edges:
        grad_ij = r[i] - r[j]
        grad[(i, j)] = grad_ij
        curl[(i, j)] = f[(i, j)] - grad_ij

    return grad, curl


def transitive_l2_norm(edges, f, r):
    grad, _ = hhd_decomposition(edges, f, r)
    return np.sqrt(sum(grad[(i, j)]**2 for (i, j) in edges))

def intransitive_l2_norm(edges, f, r):
    c_sq = 0.0

    for (i, j) in edges:
        c_ij = f[(i, j)] - (r[i] - r[j])
        c_sq += c_ij**2

    return np.sqrt(c_sq)

def total_l2_norm(edges, f, r):
    return np.sqrt(sum(f[(i, j)]**2 for (i, j) in edges))


def load_graph_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    edges = [tuple(edge) for edge in data['edges']]
    weights = data['weights']
    
    # Convert weights to log-odds
    f = {}
    for (i, j) in edges:
        key = f"{i}->{j}"
        p = weights[key]
        if p == 0:
            f[(i, j)] = -10.0
        elif p == 1:
            f[(i, j)] = 10.0
        else:
            f[(i, j)] = np.log(p / (1 - p))
        f[(j, i)] = -f[(i, j)]
    
    return nodes, edges, f


def analyze_graph(json_file, verbose=False):
    print(f"\nAnalyzing graph from: {json_file}")
    print("=" * 60)
    
    nodes, edges, f = load_graph_data(json_file)
    print(f"Number of nodes: {len(nodes)}")
    print(f"Number of edges: {len(edges)}")
    
    r = hhd_ratings_unweighted(nodes, edges, f)
    
    vorticities = {node: 0.0 for node in nodes}
    for (i, j) in edges:
        curl_ij = f[(i, j)] - (r[i] - r[j])
        vorticities[i] += curl_ij
        vorticities[j] -= curl_ij
    
    grad, curl = hhd_decomposition(edges, f, r) # curl is not properly calculated here, it requirses a spanning tree and a cycle basis
    
    l2_curl = intransitive_l2_norm(edges, f, r)
    l2_grad = transitive_l2_norm(edges, f, r)
    l2_total = total_l2_norm(edges, f, r)
    
    intransitivity_ratio = l2_curl / l2_total if l2_total > 0 else 0
    
    print(f"\n{'Intransitivity Analysis':^60}")
    print("-" * 60)
    print(f"L2 norm of intransitive component: {l2_curl:.6f}")
    print(f"L2 norm of transitive component:   {l2_grad:.6f}")
    print(f"L2 norm of total flow:              {l2_total:.6f}")
    print(f"Intransitivity ratio:               {intransitivity_ratio:.4f} ({intransitivity_ratio*100:.2f}%)")
    
    if verbose:
        print(f"\n{'Node Rankings (sorted by rating)':^60}")
        print("-" * 60)
        sorted_nodes = sorted(r.items(), key=lambda x: x[1], reverse=True)
        for rank, (node, rating) in enumerate(sorted_nodes, 1):
            print(f"{rank:2d}. {node:20s} rating: {rating:8.4f}  vorticity: {vorticities[node]:8.4f}")
    
    results = {
        'nodes': nodes,
        'ratings': r,
        'vorticities': vorticities,
        'l2_intransitive': l2_curl,
        'l2_transitive': l2_grad,
        'l2_total': l2_total,
        'intransitivity_ratio': intransitivity_ratio
    }
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python HHD.py <graph_json_file> [--verbose]")
        print("Example: python HHD.py SoccerGraphData/EPL_2425_graph.json --verbose")
        sys.exit(1)
    
    json_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    results = analyze_graph(json_file, verbose=verbose)
