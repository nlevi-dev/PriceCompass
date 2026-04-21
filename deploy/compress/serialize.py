import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from deploy.compress.compress import serialize_csv_to_bin
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("--compression", default="fflate", help="Compression method to use")
    
    args = parser.parse_args()
    serialize_csv_to_bin(args.csv_path, args.compression)
