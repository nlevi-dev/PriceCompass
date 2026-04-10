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

VENDOR = "bilkatogo.dk"

unit_lookup = {
    Unit.KG: ["/Kg."],
    Unit.L: ["/L."],
    Unit.EACH: ["/Stk."],
}

def parse_item(node, categories, name_include_description=False):
    obj = {
        "price": None,
        "unit": None,
        "country": Country.DK,
        "language": Lang.DK,
        "currency": Currency.DKK,
        "vendor": VENDOR,
        "link": None,
        "categories": categories,
        "original_name": None,
    }
    found_link = False
    found_price = False
    for n in node.descendants:
        if not found_link and n.name == "a":
            name = n.get("aria-label").lower()
            if name_include_description:
                description_text = node.find(name="p", attrs={"class": "description"})
                if description_text:
                    description_text = next(description_text.children)
                    if description_text:
                        description_text = description_text.get_text(strip=True)
                        if description_text:
                            name += " " + description_text.lower()
            obj["original_name"] = name
            txt = n.get("href")
            if not txt.startswith("http"):
                txt = "https://www."+VENDOR+txt
            obj["link"] = txt
            found_link = True
        if not found_price and isinstance(n, NavigableString):
            if len(categories) == 1 and categories[0] == Item.TOILET_PAPER:
                if " rl." in n.get_text(strip=True):
                    rolls = float(int(re.sub(r'[^\d]', "", n.get_text(strip=True))))
                    p = node.find(name="span", attrs={"class":"product-price__integer"})
                    price = float(re.sub(r'[^\d\.]', "", p.get_text(strip=True).replace(",", ".")))
                    obj["price"] = price / rolls
                    obj["unit"] = Unit.EACH
                    found_price = True
            else:
                unit = None
                for u in unit_lookup:
                    for unit_text in unit_lookup[u]:
                        if unit_text in n.get_text(strip=True):
                            unit = u
                            break
                if unit is not None:
                    obj["price"] = float(re.sub(r'[^\d\.]', "", n.get_text(strip=True).replace(",", ".")))
                    obj["unit"] = unit
                    found_price = True
        if found_link and found_price:
            break
    if found_link and found_price:
        return obj
    return None

def accept_cookies(page):
    page.get_by_role("button", name="Accepter alle").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def load_more(page):
    button = page.get_by_role("button", name="Indlæs flere")
    if button.is_visible():
        button.click()
        page.wait_for_timeout(1000)

def get_items_base(url, categories, name_include_description, use_cache = True, cache_time = None):
    cache_name = re.sub(r'[^a-zA-Z0-9]', "", url)+".csv"
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            df = read_csv_raw(cache_path)
            return df
    page = BaseScraper(url, scrolling=True, post_init_action=accept_cookies, post_scroll_action=load_more).get_page()
    soup = BeautifulSoup(page, "lxml")
    nodes = soup.find_all(name="div", id="pinnedProductPLP")
    items = []
    for node in nodes:
        for child in node.children:
            item = parse_item(child, categories, name_include_description)
            if item:
                items.append(item)
    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.bilkatogo.dk/kategori/koed-og-fisk/",[Category.MEAT_AND_FISH],False),
        ("https://www.bilkatogo.dk/kategori/frugt-og-groent/frugt/",util_category_fruits,False),
        ("https://www.bilkatogo.dk/kategori/frugt-og-groent/groentsager/",util_category_vegetables,False),
        ("https://www.bilkatogo.dk/kategori/mejeri-og-koel/mejeri/maelk/",[Item.MILK],False),
        ("https://www.bilkatogo.dk/kategori/mejeri-og-koel/mejeri/ost/",[Item.CHEESE],False),
        ("https://www.bilkatogo.dk/kategori/mejeri-og-koel/mejeri/smoer-og-fedtstof/smoer/",[Item.BUTTER],False),
        ("https://www.bilkatogo.dk/kategori/mejeri-og-koel/aeg-og-gaer/aeg/",[Item.EGG],False),
        ("https://www.bilkatogo.dk/kategori/broed-og-kager/bagerens-broed-og-kager/bagerens-broed/lyst-og-groft-broed/",[Item.BREAD],False),
        ("https://www.bilkatogo.dk/kategori/broed-og-kager/lyst-og-groft-broed/toastbroed/?attributes=Glutenfri",[Item.GLUTEN_FREE_BREAD],False),
        ("https://www.bilkatogo.dk/kategori/drikkevarer/vand-og-danskvand/",[Item.WATER],False),
        ("https://www.bilkatogo.dk/kategori/drikkevarer/sodavand/cola/",[Item.COKE],False),
        ("https://www.bilkatogo.dk/kategori/drikkevarer/energidrikke-og-sportsdrikke/energidrikke/",[Item.ENERGY_DRINK],True),
        ("https://www.bilkatogo.dk/kategori/drikkevarer/oel/",[Item.BEER],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/mel-sukker-og-bagning/mel/",[Item.FLOUR],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/mel-sukker-og-bagning/sukker-sirup-og-syltning/sukker-farin-og-flormelis/",[Item.SUGAR],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/konserves-bouillon-og-krydderier/krydderier-bouillon-og-fond/salt/",[Item.SALT],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/olie-eddike-dressing-og-sauce/olie/",[Item.OLIVE_OIL,Item.SUNFLOWER_OIL],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/pasta-ris-og-baelgfrugter/ris/",[Item.RICE],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/pasta-ris-og-baelgfrugter/pasta/",[Item.SPAGHETTI_PASTA],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/konserves-bouillon-og-krydderier/boenner-kikaerter-og-linser/",[Item.RED_BEANS_CAN],False),
        ("https://www.bilkatogo.dk/kategori/kolonial/konserves-bouillon-og-krydderier/konserveret-frugt-og-groent/majs-og-babymajs/",[Item.CRUMBLED_SWEET_CORN_CAN],False),
        ("https://www.bilkatogo.dk/kategori/personlig-pleje/haarprodukter/shampoo/",[Item.SHAMPOO],False),
        ("https://www.bilkatogo.dk/kategori/personlig-pleje/kropspleje/haandsaebe-og-haanddesinfektion/",[Item.SOAP],False),
        ("https://www.bilkatogo.dk/kategori/personlig-pleje/tandpleje/tandpasta/tandpasta-til-voksne/",[Item.TOOTHPASTE],False),
        ("https://www.bilkatogo.dk/kategori/personlig-pleje/toiletartikler/bind-tamponer-og-trusseindlaeg/tamponer/",[Item.TAMPON],False),
        ("https://www.bilkatogo.dk/kategori/personlig-pleje/sex-og-samliv/kondomer/",[Item.CONDOM],False),
        ("https://www.bilkatogo.dk/kategori/husholdning/toiletpapir-og-koekkenrulle/toiletpapir/",[Item.TOILET_PAPER],False),
    ]
    dfs = []
    for url, categories, name_include_description in urls:
        dfs.append(get_items_base(url, categories, name_include_description, use_cache=use_cache, cache_time=cache_time))
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