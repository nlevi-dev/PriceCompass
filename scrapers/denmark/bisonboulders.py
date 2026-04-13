import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "bison-boulders.com"

unit_lookup = {
    Unit.EACH: ["day ticket"],
    Unit.MONTHLY: ["30 days pass","monthly"],
    Unit.YEARLY: ["yearly"],
}

def parse_item1(node, categories, url, place):
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
    node = node.contents[0].contents[0]
    rows = node.find_all("div", attrs={"class":"sqs-block website-component-block sqs-block-website-component sqs-block-html html-block"}, recursive=False)
    for row in rows:
        cols = row.find("div").find("div").find("div").contents
        name = cols[0].get_text(strip=True).lower()
        price = None
        for c in cols[1:]:
            p = c.get_text(strip=True).lower()
            if "adults" in p:
                price = p
                break
        item = obj.copy()
        item["original_name"] = place+"adult "+name
        item["price"] = float(int(re.sub(r'\(.+\)|\D', "", price)))
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

def parse_item2(node, categories, url, place):
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
    names = []
    names.append(node.find("div", attrs={"class":"fe-block fe-block-yui_3_17_2_1_1758619848505_12959"}).get_text(strip=True).lower())
    names.append(node.find("div", attrs={"class":"fe-block fe-block-9818e66b7d5fc38e9a15"}).get_text(strip=True).lower())
    t = node.find("div", attrs={"class":"fe-block fe-block-yui_3_17_2_1_1758619848505_36496"}).get_text(strip=True).lower()
    prices = []
    prices.append(node.find("div", attrs={"class":"fe-block fe-block-68d28f91afdb31b8877601ae"}).get_text(strip=True).lower())
    prices.append(node.find("div", attrs={"class":"fe-block fe-block-2b997bbec459b509c5d8"}).get_text(strip=True).lower())
    for i in range(2):
        item = obj.copy()
        item["original_name"] = place+t+" "+names[i]+" subscription"
        item["price"] = float(int(re.sub(r'\D', "", prices[i])))
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

def get_items_base(url, categories, place, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    items = []

    page = BaseScraper(url, scrolling=False).get_page()
    soup = BeautifulSoup(page, "lxml")
    
    if "prices" in url:
        node = soup.find(name="div", id="page-section-689217040da0db6d7f3b9489")
        items += parse_item1(node, categories, url, place)
    elif "membership-list" in url:
        node = soup.find(name="div", attrs={"class":"fluid-engine fe-68d28f91fdf3cb98042659ad"})
        items += parse_item2(node, categories, url, place)

    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.bison-boulders.com/prices",[Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP],"bisonboulders "),
        ("https://www.bison-boulders.com/membership-list",[Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP,Item.CLIMBING_GYM_YEARLY_MEMBERSHIP],"bisonboulders "),
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