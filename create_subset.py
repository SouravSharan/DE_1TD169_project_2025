import argparse

def copy_first_n_lines(input_file, output_file, n=10000):
    """Copies the first `n` lines from input_file to output_file."""
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for i, line in enumerate(infile):
            if i >= n:
                break  # Stop after n lines
            outfile.write(line)  # Write line to output file

def main():
    parser = argparse.ArgumentParser(description="Copy the first N lines from a JSON file to a new file.")
    parser.add_argument("input_file", help="Path to the input JSON file")
    parser.add_argument("output_file", help="Path to the output JSON file")
    parser.add_argument("-n", "--num_lines", type=int, default=10000, help="Number of lines to copy (default: 10000)")
    
    args = parser.parse_args()
    
    copy_first_n_lines(args.input_file, args.output_file, args.num_lines)
    print(f"Successfully copied {args.num_lines} lines from '{args.input_file}' to '{args.output_file}'.")

if __name__ == "__main__":
    main()
