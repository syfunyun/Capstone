import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_ic_vs_real_rank(metrics_csv, real_csv, real_rank_col):
    # Load node metrics and real ranking files
    metrics_df = pd.read_csv(metrics_csv)
    real_df = pd.read_csv(real_csv)

    # Ensure columns exist
    if 'Node' not in metrics_df.columns or 'Intransitivity_Centrality' not in metrics_df.columns:
        raise ValueError(f"metrics_csv must contain 'Node' and 'Intransitivity_Centrality' columns.")
    if 'Node' not in real_df.columns or real_rank_col not in real_df.columns:
        raise ValueError(f"real_csv must contain 'Node' and '{real_rank_col}' columns.")

    # Merge on Node
    merged = pd.merge(real_df[['Node', real_rank_col]], metrics_df[['Node', 'Intransitivity_Centrality']], on='Node', how='inner')
    merged = merged.dropna(subset=[real_rank_col, 'Intransitivity_Centrality'])

    # Sort by real rank (ascending) and ensure integer type for plotting
    merged[real_rank_col] = pd.to_numeric(merged[real_rank_col], errors='coerce').astype(int)
    merged = merged.sort_values(real_rank_col)

    # Plot as a line with diamond markers, no shifting
    plt.rcParams['font.family'] = 'monospace'
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        merged[real_rank_col],
        merged['Intransitivity_Centrality'],
        color="#9A78DA",
        marker='D',
        markersize=8,
        linestyle='-',
        linewidth=2
    )
    # Draw a dashed line at IC score = 0
    ax.axhline(0, color='lightgrey', linewidth=1, linestyle='--', zorder=1)
    ax.set_xticks(merged[real_rank_col])
    ax.set_xticklabels(merged[real_rank_col].astype(int))
    ax.set_xlabel(f"Real Rank ({real_rank_col})", fontfamily='monospace')
    ax.set_ylabel("Intransitivity Centrality", fontfamily='monospace')
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.tick_params(axis='x', colors='#333333', rotation=45)
    ax.tick_params(axis='y', colors='#333333')
    plt.tight_layout()
    # Save with a descriptive name
    base_metrics = os.path.splitext(os.path.basename(metrics_csv))[0]
    base_real = os.path.splitext(os.path.basename(real_csv))[0]
    out_file = f"real_ranking_icscore_{real_rank_col}_from_{base_real}_and_{base_metrics}.png"
    plt.savefig(out_file, dpi=300)
    print(f"Saved plot as {out_file}")
    # Plot Real Rank vs Upset Rate
    if 'Upset_rate' in metrics_df.columns:
        merged_upset = pd.merge(real_df[['Node', real_rank_col]], metrics_df[['Node', 'Upset_rate']], on='Node', how='inner')
        merged_upset = merged_upset.dropna(subset=[real_rank_col, 'Upset_rate'])
        merged_upset[real_rank_col] = pd.to_numeric(merged_upset[real_rank_col], errors='coerce').astype(int)
        merged_upset = merged_upset.sort_values(real_rank_col)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        plt.rcParams['font.family'] = 'monospace'
        ax2.plot(
            merged_upset[real_rank_col],
            merged_upset['Upset_rate'],
            color="#50e450",
            marker='D',
            markersize=8,
            linestyle='-',
            linewidth=2
        )
        ax2.set_xticks(merged_upset[real_rank_col])
        ax2.set_xticklabels(merged_upset[real_rank_col].astype(int))
        ax2.set_xlabel(f"Real Rank ({real_rank_col})", fontfamily='monospace')
        ax2.set_ylabel("Upset Rate", fontfamily='monospace')
        ax2.set_title("Upset Rate vs Real Rank", fontfamily='monospace')
        ax2.grid(False)
        for spine in ax2.spines.values():
            spine.set_color('#333333')
        ax2.xaxis.label.set_color('#333333')
        ax2.yaxis.label.set_color('#333333')
        ax2.tick_params(axis='x', colors='#333333', rotation=45)
        ax2.tick_params(axis='y', colors='#333333')
        plt.tight_layout()
        out_file2 = f"real_ranking_upsetrate_{real_rank_col}_from_{base_real}_and_{base_metrics}.png"
        plt.savefig(out_file2, dpi=300)
        print(f"Saved plot as {out_file2}")
    plt.show()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: python real_ranking_plots.py <node_metrics_csv> <real_ranking_csv> <real_rank_col>")
        print("Example: python real_ranking_plots.py node_metrics_EPL_2021_graph.csv real_ranking_EPL.csv rank_2021")
        sys.exit(1)
    metrics_csv = sys.argv[1]
    real_csv = sys.argv[2]
    real_rank_col = sys.argv[3]
    plot_ic_vs_real_rank(metrics_csv, real_csv, real_rank_col)
