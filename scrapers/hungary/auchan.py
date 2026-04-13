import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup, NavigableString

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Category, util_category_fruits, util_category_vegetables, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "auchan.hu"

unit_lookup = {
    Unit.KG: [r"\d/kg",r"\xa0Ft/kg"],
    Unit.L: [r"\d/l",r"\xa0Ft/l"],
    Unit.EACH: [r"\d/db",r"\xa0Ft/db"],
}

def parse_item(node, categories, lang=Lang.EN):
    obj = {
        "price": None,
        "unit": None,
        "country": Country.HU,
        "language": lang,
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
                txt = "https://www."+VENDOR+txt
            obj["link"] = txt
            found_link = True
        if not found_price and isinstance(n, NavigableString):
            unit = None
            for u in unit_lookup:
                for unit_text in unit_lookup[u]:
                    if re.search(unit_text, n.get_text(strip=True)):
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
    page.get_by_role("button", name="Összes süti elfogadása").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def accept_cookies2(page):
    page.wait_for_timeout(10000)
    page.dispatch_event(".om-popup-close-x", "click")
    page.wait_for_load_state("networkidle", timeout=5000)
    page.get_by_role("button", name="Összes süti elfogadása").click()
    page.wait_for_load_state("networkidle", timeout=5000)

# page dynamically unloads as you scroll
global pages
pages = []

def load_more(page):
    global pages
    pages.append(page.content())
    button = page.get_by_role("button", name="Loading more products")
    if button.is_visible():
        button.click()
        page.wait_for_timeout(1000)

def load_more2(page):
    global pages
    pages.append(page.content())
    button = page.get_by_role("button", name="További termékek betöltése")
    if button.is_visible():
        button.click()
        page.wait_for_timeout(1000)

def get_items_base(url, categories, lang = Lang.EN, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    global pages
    pages = []
    if lang == Lang.HU:
        page = BaseScraper(url, scrolling=True, post_init_action=accept_cookies2, post_scroll_action=load_more2).get_page()
    else:
        page = BaseScraper(url, scrolling=True, post_init_action=accept_cookies,  post_scroll_action=load_more ).get_page()
    items = []
    for page in pages:
        soup = BeautifulSoup(page, "lxml")
        nodes = soup.find_all(name="ul", attrs={"role": "feed"})
        for node in nodes:
            for child in node.children:
                item = parse_item(child, categories, lang=lang)
                if item:
                    items.append(item)
    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://auchan.hu/en/shop/fresh-food/meat-cold-cuts-fish/packaged-meats.c-6606",[Category.MEAT_AND_FISH],Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/fruits-and-vegetables/fruit.c-5681",util_category_fruits,Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/fruits-and-vegetables/vegetable.c-5685",util_category_vegetables,Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/dairy-products-egg-cheese/milks-milk-drinks.c-6537?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25226538%2522%255D%257D%257D",[Item.MILK],Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/dairy-products-egg-cheese/packaged-cheese.c-5680",[Item.CHEESE],Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/dairy-products-egg-cheese/butter-butter-spread-and-margarine.c-5678",[Item.BUTTER],Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/dairy-products-egg-cheese/egg.c-5676",[Item.EGG],Lang.EN),
        ("https://auchan.hu/en/shop/fresh-food/pastries-and-breads/bread.c-5652?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25226166%2522%255D%257D%257D",[Item.BREAD],Lang.EN),
        ("https://auchan.hu/en/shop/conscious-nutrition/special-diet/gluten-free-products.c-5594?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25225889%2522%255D%257D%257D",[Item.GLUTEN_FREE_BREAD],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/mineral-water-soft-drink-syrup/mineral-water.c-5636?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25229392%2522%255D%257D%257D",[Item.WATER],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/mineral-water-soft-drink-syrup/soft-drinks.c-5645?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25226128%2522%255D%257D%257D",[Item.COKE],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/mineral-water-soft-drink-syrup/energy-drinks.c-5638?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25226089%2522%255D%257D%257D",[Item.ENERGY_DRINK],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/beers-ciders/.c-14818",[Item.BEER],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/beers-ciders/.c-15284",[Item.BEER],Lang.EN),
        ("https://auchan.hu/en/shop/drinks/beers-ciders/.c-15293",[Item.BEER],Lang.EN),
        ("https://auchan.hu/en/shop/sustainable-food/basic-foods/flour-sugar-breadcrumbs.c-6613",[Item.FLOUR,Item.SUGAR],Lang.EN),
        ("https://auchan.hu/shop/tartos-elelmiszer/etelizesites-instant-alapok/etelizesites-fuszerek/so.c-5689",[Item.SALT],Lang.HU),
        ("https://auchan.hu/en/shop/sustainable-food/basic-foods/oil-vinegar.c-6612",[Item.OLIVE_OIL,Item.SUNFLOWER_OIL],Lang.EN),
        ("https://auchan.hu/en/shop/sustainable-food/basic-foods/rice-pasta.c-5569",[Item.RICE,Item.SPAGHETTI_PASTA],Lang.EN),
        ("https://auchan.hu/en/shop/sustainable-food/basic-foods/canned-food-and-pickles.c-5565?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25225709%2522%255D%257D%257D",[Item.RED_BEANS_CAN,Item.CRUMBLED_SWEET_CORN_CAN],Lang.EN),
        ("https://auchan.hu/en/shop/beauty-health-baby/beauty-care/bathing/mens-shower-gel.c-6199",[Item.SHAMPOO],Lang.EN),
        ("https://auchan.hu/en/shop/beauty-health-baby/beauty-care/soap/liquid-soap.c-7108",[Item.SOAP],Lang.EN),
        ("https://auchan.hu/en/shop/beauty-health-baby/beauty-care/mouth-care/toothpaste.c-6228",[Item.TOOTHPASTE],Lang.EN),
        ("https://auchan.hu/en/shop/beauty-health-baby/health-hygiene/womens-hygiene.c-5663?qq=%257B%2522filterParams%2522%253A%257B%2522subcategory%2522%253A%255B%25226219%2522%255D%257D%257D",[Item.TAMPON],Lang.EN),
        ("https://auchan.hu/en/shop/beauty-health-baby/health-hygiene/pharmacy/sexual-well-being.c-6224",[Item.CONDOM],Lang.EN),
        ("https://auchan.hu/en/shop/home-chemical-and-household-paper/household-items-chemicals-and-stationary/household-paper-products/toilet-paper.c-5962",[Item.TOILET_PAPER],Lang.EN),
    ]
    dfs = []
    for url, categories, lang in urls:
        dfs.append(get_items_base(url, categories, lang=lang, use_cache=use_cache, cache_time=cache_time))
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