import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup, NavigableString

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Category, util_category_fruits, util_category_vegetables, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "tesco.hu"

unit_lookup = {
    Unit.KG: ["\xa0Ft/kg"],
    Unit.L: ["\xa0Ft/litre"],
    Unit.EACH: ["\xa0Ft/each"],
}

def parse_item(node, categories):
    obj = {
        "price": None,
        "unit": None,
        "country": Country.HU,
        "language": Lang.EN,
        "currency": Currency.HUF,
        "vendor": VENDOR,
        "link": None,
        "categories": categories,
        "original_name": None,
    }
    found_link = False
    found_price = False
    for n in node.descendants:
        if not found_link and n.name == "a":
            obj["original_name"] = n.get_text(strip=True).lower()
            txt = n.get("href")
            if not txt.startswith("http"):
                txt = "https://www.bevasarlas."+VENDOR+txt
            obj["link"] = txt
            found_link = True
        if not found_price and isinstance(n, NavigableString):
            unit = None
            for u in unit_lookup:
                for unit_text in unit_lookup[u]:
                    if unit_text in n.get_text(strip=True):
                        unit = u
                        break
            if unit is not None:
                obj["price"] = float(int(re.sub(r'\D', "", n.get_text(strip=True))))
                obj["unit"] = unit
                found_price = True
        if found_link and found_price:
            break
    if found_link and found_price:
        return obj
    return None

def accept_cookies(page):
    page.get_by_role("button", name="Accept all").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    page = BaseScraper(url, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    nodes = soup.find_all(name="ul", id="list-content")
    items = []
    for node in nodes:
        for child in node.children:
            item = parse_item(child, categories)
            if item:
                items.append(item)
    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/meat-and-delicatessen/fresh-prepacked-meat?sortBy=relevance&count=512",[Category.MEAT_AND_FISH]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/fruit-and-vegetable/fruits?sortBy=relevance&count=512",util_category_fruits),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/fruit-and-vegetable/vegetables?sortBy=relevance&count=512",util_category_vegetables),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/dairy-eggs/milk-and-milk-drinks/fresh-milk?sortBy=relevance&count=512",[Item.MILK]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/dairy-eggs/cheese-and-curds?sortBy=relevance&count=512",[Item.CHEESE]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/dairy-eggs/butter-margarine-and-spreads/butter-and-spreads?sortBy=relevance&count=512",[Item.BUTTER]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/dairy-eggs/eggs?sortBy=relevance&count=512",[Item.EGG]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/bakery/fresh-bakery/bread?sortBy=relevance&count=512",[Item.BREAD]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/bakery/gluten-free?sortBy=relevance&count=512",[Item.GLUTEN_FREE_BREAD]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drinks/water?sortBy=relevance&count=512",[Item.WATER]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drinks/soft-drinks/carbonated-soft-drinks?sortBy=relevance&count=512",[Item.COKE]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drinks/soft-drinks/energy-and-sport-drinks/energy-drinks/all?sortBy=relevance&count=512",[Item.ENERGY_DRINK]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drinks/beer-and-cider?sortBy=relevance&count=512",[Item.BEER]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/food-cupboard/all?sortBy=relevance&count=512",[Category.PANTRY_STAPLES]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drugstore/mens-toiletries/sampoo-for-men?sortBy=relevance&count=512",[Item.SHAMPOO]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drugstore/bath-and-handwash-products/liquid-soaps?sortBy=relevance&count=512",[Item.SOAP]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drugstore/oral-care/toothpaste?sortBy=relevance&count=512",[Item.TOOTHPASTE]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drugstore/personal-hygiene/tampons?sortBy=relevance&count=512",[Item.TAMPON]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/drugstore/health-care/condoms/all?sortBy=relevance&count=512",[Item.CONDOM]),
        ("https://bevasarlas.tesco.hu/groceries/en-HU/shop/household/household-paper/toilet-paper/all?sortBy=relevance&count=512",[Item.TOILET_PAPER]),
    ]
    dfs = []
    for url, categories in urls:
        dfs.append(get_items_base(url, categories, use_cache=use_cache, cache_time=cache_time))
    df = pd.concat(dfs, ignore_index=True).drop_duplicates("original_name", keep="first", ignore_index=True)
    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df = raw_items_to_df(df)
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