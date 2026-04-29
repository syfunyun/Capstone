import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
import json
import sys
import random
import networkx as nx


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
    tran = {}
    cycl = {}

    for (i, j) in edges:
        tran_ij = r[i] - r[j]
        tran[(i, j)] = tran_ij
        cycl[(i, j)] = f[(i, j)] - tran_ij

    return tran, cycl


def transitive_l2_norm(edges, f, r):
    tran, _ = hhd_decomposition(edges, f, r)
    return np.sqrt(sum(tran[(i, j)]**2 for (i, j) in edges))

def intransitive_l2_norm(edges, f, r):
    c_sq = 0.0

    for (i, j) in edges:
        c_ij = f[(i, j)] - (r[i] - r[j])
        c_sq += c_ij**2

    return np.sqrt(c_sq)

def total_l2_norm(edges, f, r):
    return np.sqrt(sum(f[(i, j)]**2 for (i, j) in edges))


def calculate_basis_cycles(nodes, edges, f, r, verbose=False):
    import networkx as nx
    import random
    #random.seed(2)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    root = random.choice(nodes)
    if verbose:
        print(f"Selected root node for spanning tree: {root}")
    TU = nx.minimum_spanning_tree(G)
    tree_edges = set(TU.edges())
    if verbose:
        print(f"Spanning tree edges: {tree_edges}")
    all_edges_set = set((min(i, j), max(i, j)) for (i, j) in edges)
    tree_edges_set = set((min(i, j), max(i, j)) for (i, j) in tree_edges)
    non_tree_edges = all_edges_set - tree_edges_set
    if verbose:
        print(f"Non-tree (cycle) edges: {non_tree_edges}")
    basis_cycles = []
    for (i, j) in non_tree_edges:
        path = nx.shortest_path(TU, source=j, target=i)
        cycle_nodes = path + [j]
        cycle_edges = [(cycle_nodes[k], cycle_nodes[k+1]) for k in range(len(cycle_nodes)-1)]
        if verbose:
            print(f"Cycle for edge ({i}, {j}): {cycle_edges}")
        vorticity = 0.0
        for u, v in cycle_edges:
            if (u, v) in f:
                cycl_uv = f[(u, v)] - (r[u] - r[v])
                if verbose:
                    print(f"  Edge ({u}, {v}): flow = {f[(u, v)]:.6f}, rating diff = {r[u] - r[v]:.6f}, cycl = {cycl_uv:.6f} (forward)")
                vorticity += cycl_uv
            elif (v, u) in f:
                cycl_vu = f[(v, u)] - (r[v] - r[u])
                if verbose:
                    print(f"  Edge ({u}, {v}): flow = {f[(v, u)]:.6f}, rating diff = {r[v] - r[u]:.6f}, cycl = {-cycl_vu:.6f} (reverse)")
                vorticity += -cycl_vu
            else:
                if verbose:
                    print(f"  Edge ({u}, {v}): MISSING in f!")
        if verbose:
            print(f"Vorticity for cycle ({i}, {j}): {vorticity}")
        basis_cycles.append({
            'cycle_nodes': cycle_nodes,
            'cycle_edges': cycle_edges,
            'vorticity': vorticity
        })
    basis_cycles.sort(key=lambda c: c['vorticity'])
    return basis_cycles


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

    basis_cycles = calculate_basis_cycles(nodes, edges, f, r, verbose=verbose)

    l2_cycl = intransitive_l2_norm(edges, f, r)
    l2_tran = transitive_l2_norm(edges, f, r)
    l2_total = total_l2_norm(edges, f, r)
    intransitivity_ratio = l2_cycl / l2_total if l2_total > 0 else 0

    print(f"\n{'Intransitivity Analysis':^60}")
    print("-" * 60)
    print(f"L2 norm of cyclic component:      {l2_cycl:.6f}")
    print(f"L2 norm of transitive component:  {l2_tran:.6f}")
    print(f"L2 norm of total flow:            {l2_total:.6f}")
    print(f"Intransitivity ratio:             {intransitivity_ratio:.4f} ({intransitivity_ratio*100:.2f}%)")

    if verbose:
        print(f"\n{'Node Rankings (sorted by rating)':^60}")
        print("-" * 60)
        sorted_nodes = sorted(r.items(), key=lambda x: x[1])
        for rank, (node, rating) in enumerate(sorted_nodes, 1):
            print(f"{rank:2d}. {node:20s} rating: {rating:8.4f}")
    results = {
        'nodes': nodes,
        'ratings': r,
        'basis_cycles': basis_cycles,
        'l2_intransitive': l2_cycl,
        'l2_transitive': l2_tran,
        'l2_total': l2_total,
        'intransitivity_ratio': intransitivity_ratio
    }
    return results



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python HHD.py <graph_json_file> [--verbose]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    results = analyze_graph(json_file, verbose=verbose)
