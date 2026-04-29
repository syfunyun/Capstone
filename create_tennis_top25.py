import os
import pandas as pd

# List of input files and corresponding output names
input_files = [
    "TennisTop300in2010/node_metrics_atp_tennis_graph.csv",
    "TennisTop25in2025/node_metrics_atp_tennis_graph.csv",
    "TennisTop100in2005/node_metrics_atp_tennis_graph.csv"
]
output_names = [
    "top25_2010.csv",
    "top25_2025.csv",
    "top25_2005.csv"
]

# Create output directory if it doesn't exist
output_dir = "TennisAllTop25"
os.makedirs(output_dir, exist_ok=True)

for infile, outname in zip(input_files, output_names):
    # Read CSV
    df = pd.read_csv(infile)
    # Drop rows with missing Intransitivity_Centrality
    df = df.dropna(subset=["Intransitivity_Centrality"])
    # Sort by Intransitivity_Centrality increasing (lowest to highest)
    df_sorted = df.sort_values("Intransitivity_Centrality", ascending=True)
    # Select top 25
    top25 = df_sorted.head(25)
    # Rename columns
    top25 = top25.rename(columns={"Node": "Player"})
    # Keep only Player and Intransitivity_Centrality columns
    top25 = top25[["Player", "Intransitivity_Centrality"]]
    # Write to CSV
    top25.to_csv(os.path.join(output_dir, outname), index=False)
