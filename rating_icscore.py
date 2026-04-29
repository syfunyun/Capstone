import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_rating_vs_ic(csv_file):
    df = pd.read_csv(csv_file)
    rating_col = 'HHD_Rating'
    ic_col = 'Intransitivity_Centrality'
    if ic_col not in df.columns or rating_col not in df.columns:
        raise ValueError(f"Could not find rating or IC score columns in {csv_file}. Columns found: {df.columns.tolist()}")
    rating = df[rating_col]
    ic_score = df[ic_col]

    plt.rcParams['font.family'] = 'monospace'
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlabel('HHD Rating', fontfamily='monospace')
    ax.set_ylabel('Intransitivity Centrality', fontfamily='monospace')
    ax.set_title('HHD Rating vs Intransitivity Centrality', fontfamily='monospace', color='#333333')
    ax.grid(False)
    ax.axhline(0, color='lightgrey', linewidth=1, linestyle='--', alpha=0.9)
    ax.axvline(0, color='lightgrey', linewidth=1, linestyle='--', alpha=0.9)
    ax.scatter(rating, ic_score, color="#9A78DA", s=80, zorder=3)  # light purple
    # Set axis spines and tick/label text to dark grey
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.tick_params(axis='x', colors='#333333')
    ax.tick_params(axis='y', colors='#333333')

    plt.tight_layout()
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    out_file = f"rating_vs_ic_{base_name}.png"
    plt.savefig(out_file, dpi=300)
    print(f"Saved plot as {out_file}")
    plt.show()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python rating_icscore.py <node_metrics_csv>")
        sys.exit(1)
    csv_file = sys.argv[1]
    plot_rating_vs_ic(csv_file)
