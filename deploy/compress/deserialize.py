import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from deploy.compress.utils import deserialize_df
import argparse

def deserialize_bin_to_csv(bin_path, compression=None):
    with open(bin_path, "rb") as f:
        byte_data = f.read()
    df = deserialize_df(byte_data, compression=compression)[1]
    csv_path = bin_path[:bin_path.rfind(".")]+".csv"
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bin_path", help="Path to the binary file")
    parser.add_argument("--compression", default="fflate", help="Compression method to use")
    
    args = parser.parse_args()
    deserialize_bin_to_csv(args.bin_path, args.compression)
