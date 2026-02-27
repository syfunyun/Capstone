import sys
import os
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_soccer.py <csv_file> [--verbose]")
        print("Example: python analyze_soccer.py SoccerRawData/EPL_2425.csv --verbose")
        print("\nThis script will:")
        print("  1. Generate graph data from the CSV file")
        print("  2. Run HHD analysis on the generated graph")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Validate input file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    graph_file = f"SoccerGraphData/{base_name}_graph.json"
    
    print("=" * 70)
    print(f"STEP 1: Generating graph from {csv_file}")
    print("=" * 70)
    
    # Run generate_graph.py
    result = subprocess.run(
        [sys.executable, "generate_graph.py", csv_file, graph_file],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("\nError: Graph generation failed")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print(f"STEP 2: Running HHD analysis on {graph_file}")
    print("=" * 70)
    
    # Run HHD.py
    hhd_args = [sys.executable, "HHD.py", graph_file]
    if verbose:
        hhd_args.append("--verbose")
    
    result = subprocess.run(hhd_args, capture_output=False)
    
    if result.returncode != 0:
        print("\nError: HHD analysis failed")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
