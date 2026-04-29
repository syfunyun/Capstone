import sys
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_hhd_vs_real(node_metrics_csv, real_ranking_csv, real_rank_col='Real_Rank', hhd_col='HHD_Rating'):
    # Load data
    metrics_df = pd.read_csv(node_metrics_csv)
    real_df = pd.read_csv(real_ranking_csv)

    # Ensure columns exist
    if 'Node' not in metrics_df.columns or hhd_col not in metrics_df.columns:
        raise ValueError(f"node_metrics_csv must contain 'Node' and '{hhd_col}' columns.")
    if 'Node' not in real_df.columns or real_rank_col not in real_df.columns:
        raise ValueError(f"real_ranking_csv must contain 'Node' and '{real_rank_col}' columns.")

    # Merge on Node
    merged = pd.merge(real_df[['Node', real_rank_col]], metrics_df[['Node', hhd_col]], on='Node', how='inner')
    merged = merged.dropna(subset=[real_rank_col, hhd_col])

    # Sort by real rank (ascending)
    merged[real_rank_col] = pd.to_numeric(merged[real_rank_col], errors='coerce').astype(int)
    merged = merged.sort_values(real_rank_col)

    # Plot
    plt.rcParams['font.family'] = 'monospace'
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        merged[real_rank_col],
        merged[hhd_col],
        color="#9A78DA",
        marker='D',
        markersize=8,
        linestyle='-',
        linewidth=2
    )
    ax.set_xticks(merged[real_rank_col])
    ax.set_xticklabels(merged[real_rank_col].astype(int))
    ax.set_xlabel(f"Real Rank ({real_rank_col})", fontfamily='monospace')
    ax.set_ylabel(f"HHD Rating ({hhd_col})", fontfamily='monospace')
    ax.set_title(f"HHD Rating vs Real Rank", fontfamily='monospace', color='#333333')
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.tick_params(axis='x', colors='#333333', rotation=45)
    ax.tick_params(axis='y', colors='#333333')
    plt.tight_layout()
    # Save with a descriptive name
    base_metrics = os.path.splitext(os.path.basename(node_metrics_csv))[0]
    base_real = os.path.splitext(os.path.basename(real_ranking_csv))[0]
    out_file = f"hhd_vs_real_{base_real}_{base_metrics}.png"
    plt.savefig(out_file, dpi=300)
    print(f"Saved plot as {out_file}")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python hhd_vs_real.py <node_metrics_csv> <real_ranking_csv> [real_rank_col] [hhd_col]")
        sys.exit(1)
    node_metrics_csv = sys.argv[1]
    real_ranking_csv = sys.argv[2]
    real_rank_col = sys.argv[3] if len(sys.argv) > 3 else 'Real_Rank'
    hhd_col = sys.argv[4] if len(sys.argv) > 4 else 'HHD_Rating'
    plot_hhd_vs_real(node_metrics_csv, real_ranking_csv, real_rank_col, hhd_col)
