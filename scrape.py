import traceback
import importlib.util
from pathlib import Path
from tqdm import tqdm
import multiprocessing

import pandas as pd

def process_row(args):
    module_name, script_path, use_cache, cache_time = args
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        df = module.get_items(use_cache=use_cache,cache_time=cache_time)
        return (df, None)
    except Exception as e:
        trace_list = traceback.format_exception(type(e), e, e.__traceback__)
        full_trace_string = "".join(trace_list)
        return (None, full_trace_string)

def scrape_all(use_cache = True, cache_time = None) -> pd.DataFrame:
    root_path = Path("scrapers").resolve()
    dfs = []
    tasks = []
    for script_path in root_path.rglob("*.py"):
        depth = len(script_path.relative_to(root_path).parts)
        if depth <= 1:
            continue
        module_name = f"mod_{script_path.stem}_{depth}"
        tasks.append((module_name, script_path, use_cache, cache_time))
    with multiprocessing.Pool(processes=4) as pool:
        results = list(tqdm(pool.imap_unordered(process_row, tasks), total=len(tasks)))
        for r in results:
            if r[1] is not None:
                print("\n\n======== ERROR ========")
                print(r[1])
                print("=======================\n\n")
            else:
                dfs.append(r[0])
    df = pd.concat(dfs, ignore_index=True)
    return df

if __name__ == "__main__":
    import shutil
    import argparse
    from datetime import datetime
    terminal_width, _ = shutil.get_terminal_size()
    pd.set_option('display.max_colwidth', terminal_width // 2)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', terminal_width)
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--no_cache", action="store_true", help="")
    parser.add_argument("--cache_time", type=int, required=False, help="")
    args = parser.parse_args()
    df = scrape_all(use_cache = (not args.no_cache), cache_time = args.cache_time)
    data_path = Path(__file__).resolve().parent / "data"
    data_path.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename_csv = timestamp + ".csv"
    df = df[df["price"] > 0]
    df.to_csv(data_path/filename_csv, index=False)