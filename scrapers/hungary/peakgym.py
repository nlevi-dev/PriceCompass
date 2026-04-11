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

VENDOR = "peakgym.hu"

unit_lookup = {
    Unit.EACH: ["1 alkalom"],
    Unit.MONTHLY: ["1 hónapos"],
    Unit.YEARLY: ["12 hónapos"],
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
    children = [c for c in node.children if isinstance(c, Tag)]
    name_base = ""
    for t in ["bérlet", "napijegy"]:
        if t in children[0].get_text(strip=True).lower():
            name_base += t+" "
            break
    if name_base == "":
        return items
    current_class = ""
    for row in children[1:]:
        cells = [c for c in row.children if isinstance(c, Tag)]
        if len(cells) == 3 and name_base == "bérlet ":
            current_class = cells[0].get_text(strip=True).lower()+" "
            cells = cells[1:]
        item = obj.copy()
        item["original_name"] = place+name_base+current_class+cells[0].get_text(strip=True).lower()
        item["price"] = float(int(re.sub(r'\D', "", cells[1].get_text(strip=True).lower())))
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
    page.get_by_role("button", name="Elfogadom").click()
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
    nodes = soup.find_all(name="table", attrs={"class":"table timetable"})
    items = []
    for node in nodes:
        for child in [c for c in node.children if isinstance(c, Tag)]:
            items += parse_item(child, categories, url, place)
    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://peakgym.hu/arena/arak",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP,Item.GYM_YEARLY_MEMBERSHIP],"peakgym aréna "),
        # ("https://peakgym.hu/budaors/arak",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP,Item.GYM_YEARLY_MEMBERSHIP],"peakgym budaörs "),
        # ("https://peakgym.hu/gold/arak",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP,Item.GYM_YEARLY_MEMBERSHIP],"peakgym gold "),
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