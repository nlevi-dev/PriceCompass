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

VENDOR = "budapestgym.com"

unit_lookup = {
    Unit.EACH: ["1-entry pass"],
    Unit.MONTHLY: ["normal pass"],
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
    name = node.find(name="a", attrs={"class":"elementor-toggle-title"})
    if name is None:
        return items
    name = name.get_text(strip=True).lower()
    obj["original_name"] = place+name
    price = name
    price = price[price.find("(")+1:]
    price = price[:price.find(")")]
    price = price.split("/")
    for p in price:
        if "huf" in p:
            obj["price"] = float(int(re.sub(r'\D', "", p)))
    unit = None
    for u in unit_lookup:
        for unit_text in unit_lookup[u]:
            if unit_text in obj["original_name"]:
                unit = u
                break
    if unit is not None and obj["price"] is not None:
        obj["unit"] = unit
        items.append(obj)
    return items

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
    page = BaseScraper(url, scrolling=True).get_page()
    soup = BeautifulSoup(page, "lxml")
    node = soup.find(name="div", attrs={"class":"elementor-element elementor-element-96fdc06 elementor-widget elementor-widget-toggle"})
    node = [c for c in node.children if isinstance(c, Tag)][0]
    node = [c for c in node.children if isinstance(c, Tag)][0]
    items = []
    for child in [c for c in node.children if isinstance(c, Tag)]:
        items += parse_item(child, categories, url, place)
    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://budapestgym.com/gym/",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP],"4% fitness budapest "),
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