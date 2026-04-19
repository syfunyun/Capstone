import sys
import pandas as pd
import matplotlib.pyplot as plt


def plot_upset_vs_ic(node_metrics_csv):
    df = pd.read_csv(node_metrics_csv)
    if 'Upset_rate' not in df.columns or 'Intransitivity_Centrality' not in df.columns:
        print("Input CSV must contain 'Upset_rate' and 'Intransitivity_Centrality' columns.")
        return
    plt.rcParams['font.family'] = 'monospace'
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df['Upset_rate'], df['Intransitivity_Centrality'], color="#50e450", s=80, zorder=3)
    ax.set_xlabel('Upset Rate', fontfamily='monospace')
    ax.set_ylabel('Intransitivity Centrality', fontfamily='monospace')
    ax.set_title('Upset Rate vs Intransitivity Centrality', fontfamily='monospace')
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.tick_params(axis='x', colors='#333333')
    ax.tick_params(axis='y', colors='#333333')
    plt.tight_layout()
    import os
    base = os.path.splitext(os.path.basename(node_metrics_csv))[0]
    out_file = f"upset_vs_ic_{base}.png"
    plt.savefig(out_file, dpi=300)
    print(f"Saved plot as {out_file}")
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upset_icscore.py <node_metrics_csv>")
        sys.exit(1)
    plot_upset_vs_ic(sys.argv[1])
