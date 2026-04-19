import sys
import os
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_soccer.py <input_file> [--verbose] [--subsets <k>]")
        print("  input_file: CSV file (generates graph) or JSON graph file (uses directly)")
        print("Example: python analyze_soccer.py SoccerRawData/EPL_2425.csv --verbose --subsets 2")
        print("Example: python analyze_soccer.py SoccerGraphData/EPL_2425_graph.json --subsets 1")
        print("\nThis script will:")
        print("  1. Generate graph data from CSV or load existing JSON graph")
        print("  2. Run HHD analysis on the graph")
        print("  3. Optionally run subset analysis (removing k nodes) and save to CSV")
        sys.exit(1)
    
    input_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Check for subsets option
    k = None
    if "--subsets" in sys.argv:
        idx = sys.argv.index("--subsets")
        if idx + 1 < len(sys.argv):
            try:
                k = int(sys.argv[idx + 1])
                if k < 1:
                    raise ValueError
            except ValueError:
                print(f"Error: k must be a positive integer after --subsets")
                sys.exit(1)
        else:
            print("Error: --subsets requires a value for k")
            sys.exit(1)
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Determine if input is CSV or JSON
    file_ext = os.path.splitext(input_file)[1].lower()
    if file_ext == '.csv':
        # Generate graph from CSV
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        graph_file = f"SoccerGraphData/{base_name}_graph.json"
        
        print("=" * 70)
        print(f"STEP 1: Generating graph from {input_file}")
        print("=" * 70)
        
        # Run generate_graph.py
        result = subprocess.run(
            [sys.executable, "generate_graph.py", input_file, graph_file],
            capture_output=False
        )
        
        if result.returncode != 0:
            print("\nError: Graph generation failed")
            sys.exit(1)
        
        step_num = 2
    elif file_ext == '.json':
        # Use JSON directly as graph file
        graph_file = input_file
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        print("=" * 70)
        print(f"STEP 1: Using graph from {input_file}")
        print("=" * 70)
        
        step_num = 2
    else:
        print(f"Error: Input file must be .csv or .json, got {file_ext}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print(f"STEP {step_num}: Running HHD analysis on {graph_file}")
    print("=" * 70)
    
    # Run HHD.py
    hhd_args = [sys.executable, "HHD.py", graph_file]
    if verbose:
        hhd_args.append("--verbose")
    
    result = subprocess.run(hhd_args, capture_output=False)
    
    if result.returncode != 0:
        print("\nError: HHD analysis failed")
        sys.exit(1)
    
    if k is not None:
        step_num += 1
        print("\n" + "=" * 70)
        print(f"STEP {step_num}: Running subset analysis (k={k}) on {graph_file}")
        print("=" * 70)
        
        # Run analyze_graph_subsets.py
        result = subprocess.run(
            [sys.executable, "analyze_graph_subsets.py", graph_file, str(k)],
            capture_output=False
        )
        
        if result.returncode != 0:
            print("\nError: Subset analysis failed")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
