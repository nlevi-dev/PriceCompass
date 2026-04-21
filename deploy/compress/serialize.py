import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from deploy.compress.utils import serialize_df
from scrapers.items import read_csv
import argparse

def serialize_csv_to_bin(csv_path, compression=None):
    df = read_csv(csv_path)
    byte_data = serialize_df(df, compression=compression)
    bin_path = csv_path[:csv_path.rfind(".")]+".bin"
    with open(bin_path, "wb") as f:
        f.write(byte_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("--compression", default="fflate", help="Compression method to use")
    
    args = parser.parse_args()
    serialize_csv_to_bin(args.csv_path, args.compression)