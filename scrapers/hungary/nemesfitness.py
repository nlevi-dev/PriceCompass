import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup, Tag

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "nemes-fitness.hu"

unit_lookup = {
    Unit.EACH: ["napijegy"],
    Unit.MONTHLY: ["1 hónap"],
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
    name = node.find(name="h3", attrs={"class":"elementor-icon-box-title"})
    if name is None:
        return items
    name = name.get_text(strip=True).lower()
    cats = node.find_all(name="div", attrs={"data-widget_type":"button.default"})
    for c in cats:
        sibling = c.find_previous_sibling()
        item = obj.copy()
        item["original_name"] = place+sibling.get_text(strip=True).lower()+" "+name
        item["price"] = float(int(re.sub(r'\D', "", c.get_text(strip=True).lower())))
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
    page.get_by_role("button", name="Elfogad").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, place, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    page = BaseScraper(url, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    node = soup.find(name="section", attrs={"class":"elementor-section elementor-top-section elementor-element elementor-element-0d4acec elementor-section-boxed elementor-section-height-default elementor-section-height-default"})
    node = [c for c in node.children if isinstance(c, Tag)][0]
    items = []
    for child in [c for c in node.children if isinstance(c, Tag)]:
        items += parse_item(child, categories, url, place)
    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.nemes-fitness.hu/araink/",[Item.GYM_SINGLE_ENTRANCE,Item.GYM_MONTHLY_MEMBERSHIP],"nemes fitness "),
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