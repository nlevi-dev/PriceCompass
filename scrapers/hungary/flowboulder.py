import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re
import time

import pandas as pd
from bs4 import BeautifulSoup, Tag

from scrapers.base_scraper import BaseScraper, DEFAULT_CACHE_TIME
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df, read_csv_raw

root_path = Path(__file__).resolve().parent.parent.parent

VENDOR = "flowboulder.hu"

unit_lookup = {
    Unit.EACH: ["belépőjegy"],
    Unit.MONTHLY: ["havi bérlet"],
    Unit.YEARLY: ["éves bérlet"],
}

def parse_item(node, categories, url, place):
    obj = {
        "price": None,
        "unit": None,
        "country": Country.HU,
        "language": Lang.HU,
        "currency": Currency.HUF,
        "vendor": VENDOR,
        "link": url,
        "categories": categories,
        "original_name": "",
    }
    items = []
    cols = node.find("thead").find("tr").find_all("th")
    adult_idx = None
    for i in range(len(cols)):
        if "felnőtt" in cols[i].get_text(strip=True).lower():
            adult_idx = i
            break
    if adult_idx == None:
        return items
    rows = node.find("tbody").find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        item = obj.copy()
        item["original_name"] = place+"felnőtt "+cells[0].get_text(strip=True).lower()
        item["price"] = float(int(re.sub(r'\D', "", cells[adult_idx].get_text(strip=True).lower())))
        unit = None
        for u in unit_lookup:
            for unit_text in unit_lookup[u]:
                if unit_text in item["original_name"]:
                    unit = u
                    break
        if unit is not None:
            item["unit"] = unit
            items.append(item)
    return items

def accept_cookies(page):
    page.get_by_role("button", name="Összes elfogadása").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, place, use_cache = True, cache_time = None):
    cache_name = re.sub(r'[^a-zA-Z0-9]', "", url)+".csv"
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            df = read_csv_raw(cache_path)
            return df
    page = BaseScraper(url, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    node = soup.find(name="table", attrs={"class":"table-auto"})
    items = parse_item(node, categories, url, place)
    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.flowboulder.hu/hu/araink",[Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP,Item.CLIMBING_GYM_YEARLY_MEMBERSHIP],"flowboulder "),
    ]
    dfs = []
    for url, categories, place in urls:
        dfs.append(get_items_base(url, categories, place, use_cache=use_cache, cache_time=cache_time))
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates("original_name", keep="first", ignore_index=True)
    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df = raw_items_to_df(df)
    df = df.drop_duplicates(["name","price","unit"], keep="first", ignore_index=True)
    return df

if __name__ == "__main__":
    import shutil
    import argparse
    terminal_width, _ = shutil.get_terminal_size()
    pd.set_option('display.max_colwidth', terminal_width // 2)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', terminal_width)
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--no_cache", action="store_true", help="")
    parser.add_argument("--cache_time", type=int, required=False, help="")
    args = parser.parse_args()
    print(get_items(use_cache = (not args.no_cache), cache_time = args.cache_time))