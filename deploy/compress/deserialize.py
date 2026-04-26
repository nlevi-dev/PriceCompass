import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from deploy.compress.compress import deserialize_bin_to_csv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bin_path", help="Path to the binary file")
    parser.add_argument("--compression", default="fflate", help="Compression method to use")
    
    args = parser.parse_args()
    deserialize_bin_to_csv(args.bin_path, args.compression)
