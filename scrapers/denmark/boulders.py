import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "boulders.dk"

unit_lookup = {
    Unit.EACH: ["dagsentré og udstyr"],
    Unit.MONTHLY: ["medlemskab"],
}

def parse_items(node, categories, url, place):
    obj = {
        "price": None,
        "unit": None,
        "country": Country.DK,
        "language": Lang.DK,
        "currency": Currency.DKK,
        "vendor": VENDOR,
        "link": url,
        "categories": categories,
        "original_name": "",
    }
    items = []
    cards = node.find_all("div", attrs={"class":"card"}, recursive=False)
    for card in cards:
        name = card.find("h2").get_text(strip=True).lower()
        rows = card.find_all("div", attrs={"class":"items"})
        for row in rows:
            price = row.get_text(strip=True).lower()
            if "voksen" in price:
                item = obj.copy()
                item["original_name"] = place+"voksen "+name
                item["price"] = float(int(re.sub(r'\D', "", price)))
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
    page.get_by_role("button", name="Allow all").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, place, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    items = []
    
    page = BaseScraper(url, scrolling=False, user_agent=None, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    nodes = soup.find_all(name="div", attrs={"class":"container"})
    for node in nodes:
        items += parse_items(node, categories, url, place)

    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://boulders.dk/priser",[Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP],"boulders "),
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