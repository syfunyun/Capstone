import os
import sys
import json
import pandas as pd
from generate_graph import create_soccer_graph, save_graph_data
from HHD import analyze_graph


def analyze_all_soccer_data(raw_data_folder="SoccerRawData", graph_data_folder="SoccerGraphData"):
    # Ensure output folder exists
    os.makedirs(graph_data_folder, exist_ok=True)
    
    # Find all CSV files
    csv_files = [f for f in os.listdir(raw_data_folder) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {raw_data_folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to analyze\n")
    
    # Store results
    results = []
    
    for csv_file in sorted(csv_files):
        csv_path = os.path.join(raw_data_folder, csv_file)
        base_name = os.path.splitext(csv_file)[0]
        graph_file = os.path.join(graph_data_folder, f"{base_name}_graph.json")
        
        print("=" * 70)
        print(f"Processing: {csv_file}")
        print("=" * 70)
        
        try:
            # Generate graph
            G = create_soccer_graph(csv_path)
            save_graph_data(G, graph_file)
            
            # Run HHD analysis
            analysis = analyze_graph(graph_file, verbose=False)
            
            # Store results
            results.append({
                'File': csv_file,
                'Nodes': len(analysis['nodes']),
                'Edges': len(analysis['ratings']) * (len(analysis['ratings']) - 1),  # Directed edges
                'L2_Intransitive': analysis['l2_intransitive'],
                'L2_Transitive': analysis['l2_transitive'],
                'L2_Total': analysis['l2_total'],
                'Intransitivity_Ratio': analysis['intransitivity_ratio']
            })
            
            print()
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            print()
    
    # Create summary table
    if results:
        df = pd.DataFrame(results)
        
        print("\n" + "=" * 100)
        print("SUMMARY TABLE")
        print("=" * 100)
        print(df.to_string(index=False))
        print("=" * 100)
        
        # Save to CSV
        output_file = "soccer_analysis_summary.csv"
        df.to_csv(output_file, index=False, float_format='%.6f')
        print(f"\nSummary saved to {output_file}")
        
        # Save to formatted text file
        output_txt = "soccer_analysis_summary.txt"
        with open(output_txt, 'w') as f:
            f.write("=" * 100 + "\n")
            f.write("SOCCER DATA INTRANSITIVITY ANALYSIS SUMMARY\n")
            f.write("=" * 100 + "\n\n")
            f.write(df.to_string(index=False))
            f.write("\n" + "=" * 100 + "\n")
        print(f"Summary saved to {output_txt}")


if __name__ == "__main__":
    raw_data_folder = "SoccerRawData"
    graph_data_folder = "SoccerGraphData"
    
    if len(sys.argv) >= 2:
        raw_data_folder = sys.argv[1]
    if len(sys.argv) >= 3:
        graph_data_folder = sys.argv[2]
    
    analyze_all_soccer_data(raw_data_folder, graph_data_folder)
