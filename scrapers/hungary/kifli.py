import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re
import time

import pandas as pd
from bs4 import BeautifulSoup, NavigableString

from scrapers.base_scraper import BaseScraper, DEFAULT_CACHE_TIME
from scrapers.items import Item, Category, util_category_fruits, util_category_vegetables, Unit, Country, Lang, Currency, raw_items_to_df, read_csv_raw

root_path = Path(__file__).resolve().parent.parent.parent

VENDOR = "kifli.hu"

unit_lookup = {
    Unit.KG: [" HUF/kg"],
    Unit.L: [" HUF/l"],
    Unit.EACH: [" HUF/pc"],
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
    found_name = False
    found_link = False
    found_price = False
    for n in node.descendants:
        if not found_link and n.name == "a":
            txt = n.get("href")
            if not txt.startswith("http"):
                txt = "https://www."+VENDOR+txt
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
                obj["price"] = float(int(re.sub(r'\D', "", re.sub(r'\.\d+', "", n.get_text(strip=True)))))
                obj["unit"] = unit
                found_price = True
        if not found_name and hasattr(n, "get") and n.get("data-test") == "productCard-body-name":
            obj["original_name"] = n.get_text(strip=True).lower()
            found_name = True
        if found_name and found_link and found_price:
            break
    if found_name and found_link and found_price:
        return obj
    return None

def accept_cookies(page):
    page.get_by_role("button", name="Accept All").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, use_cache = True, cache_time = None):
    cache_name = re.sub(r'[^a-zA-Z0-9]', "", url)+".csv"
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            df = read_csv_raw(cache_path)
            return df
    page = BaseScraper(url, scrolling=True, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    nodes = soup.find_all(name="div", attrs={"data-test": "subcategory"})
    if len(nodes) == 0:
        nodes = soup.find_all(name="div", attrs={"data-test": "products-grid"})[0].children
    items = []
    for node in nodes:
        for child in node.children:
            item = parse_item(child, categories)
            if item:
                items.append(item)
    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.kifli.hu/en-HU/c300114760-hus-es-hal",[Category.MEAT_AND_FISH]),
        ("https://www.kifli.hu/en-HU/c300113743-gyuemoelcs",util_category_fruits),
        ("https://www.kifli.hu/en-HU/c300113863-zoeldseg",util_category_vegetables),
        ("https://www.kifli.hu/en-HU/c300113362-tej-es-tej-alapu-ital",[Item.MILK]),
        ("https://www.kifli.hu/en-HU/c300113218-sajt",[Item.CHEESE]),
        ("https://www.kifli.hu/en-HU/c300113197-vaj-vajkrem-margarin",[Item.BUTTER]),
        ("https://www.kifli.hu/en-HU/c300113338-tojas-es-eleszto",[Item.EGG]),
        ("https://www.kifli.hu/en-HU/c300114340-friss-kenyer",[Item.BREAD]),
        ("https://www.kifli.hu/en-HU/c300116596-glutenmentes-kenyer",[Item.GLUTEN_FREE_BREAD]),
        ("https://www.kifli.hu/en-HU/c300119914-szensavas-asvanyviz",[Item.WATER]),
        ("https://www.kifli.hu/en-HU/c300119932-szensavmentes-asvanyviz",[Item.WATER]),
        ("https://www.kifli.hu/en-HU/c300113554-szensavas-ueditoital",[Item.COKE]),
        ("https://www.kifli.hu/en-HU/c300113620-energiaital",[Item.ENERGY_DRINK]),
        ("https://www.kifli.hu/en-HU/c300113068-soer-es-cider",[Item.BEER]),
        ("https://www.kifli.hu/en-HU/c300113551-liszt",[Item.FLOUR]),
        ("https://www.kifli.hu/en-HU/c300113650-cukor",[Item.SUGAR]),
        ("https://www.kifli.hu/en-HU/c300120621-so",[Item.SALT]),
        ("https://www.kifli.hu/en-HU/c300114415-olaj",[Item.OLIVE_OIL,Item.SUNFLOWER_OIL]),
        ("https://www.kifli.hu/en-HU/c300115705-rizs",[Item.RICE]),
        ("https://www.kifli.hu/en-HU/c300115687-teszta",[Item.SPAGHETTI_PASTA]),
        ("https://www.kifli.hu/en-HU/c300120233-kukorica-huevelyes-repa",[Item.RED_BEANS_CAN,Item.CRUMBLED_SWEET_CORN_CAN]),
        ("https://www.kifli.hu/en-HU/c300114937-sampon",[Item.SHAMPOO]),
        ("https://www.kifli.hu/en-HU/c300116680-folyekony-szappan",[Item.SOAP]),
        ("https://www.kifli.hu/en-HU/c300115024-fogkrem",[Item.TOOTHPASTE]),
        ("https://www.kifli.hu/en-HU/c300114997-tampon",[Item.TAMPON]),
        ("https://www.kifli.hu/en-HU/c300114979-ovszer",[Item.CONDOM]),
        ("https://www.kifli.hu/en-HU/c300115234-toalett-papir",[Item.TOILET_PAPER]),
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