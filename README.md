# Soccer Graph Analysis Pipeline

This README provides a simple step-by-step guide for running the soccer graph analysis scripts in this repository.

## 1. Data to Graph (if necessary)
Convert raw match data CSV to a graph JSON file.

```
python generate_soccer_graph.py <raw_data_csv>
```

- The output file is automatically named as `SoccerGraphData/<raw_data_csv_base>_graph.json`.

## 2. Analyze Subgraphs
Analyze subgraphs of the generated graph.

```
python analyze_graph_subsets.py <graph_json_file> <max_k>
```

## 3. Compute Node Metrics
Compute node metrics for each team/node.

```
python compute_node_metrics.py <graph_json_file> <subset_analysis_csv> [upset_rate_csv]
```

- **OPTIONAL PREREQ:** Calculate upset scores (if you want to include upset rates in node metrics):

```
python soccer_upset_rate.py <raw_data_csv> <graph_json_file>
```

## 4. Plot Rating vs Intransitivity Centrality
Plot HHD rating vs IC score for each node.

```
python rating_icscore.py <node_metrics_csv>
```

## 5. OPTIONAL: Plot Upset vs Intransitivity Centrality
Plot upset rate vs IC score for each node.

```
python upset_icscore.py <node_metrics_csv>
```

## 6. OPTIONAL: Plots Ranking vs IC and Ranking vs Upset
- **PREREQ:** Store real ranking in a CSV file (e.g., real_ranking_EPL.csv)

```
python real_ranking_plots.py <node_metrics_csv> <real_ranking_csv> <real_rank_col>
```

---

- All scripts require command-line arguments as shown above.
- Output files are automatically named based on input files.
- For more details, run each script without arguments to see usage instructions.
