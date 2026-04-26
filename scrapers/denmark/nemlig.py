import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup, NavigableString

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Category, util_category_fruits, util_category_vegetables, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "nemlig.com"

unit_lookup = {
    Unit.KG: [" kr./Kg."],
    Unit.L: [" kr./Ltr."],
    Unit.EACH: [" kr./Stk."],
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
    found_name = False
    found_link = False
    found_price = False
    for n in node.descendants:
        if not found_link and n.name == "a" and "product-card" in n.get("class"):
            txt = n.get("href")
            if not txt.startswith("http"):
                txt = "https://www."+VENDOR+txt
            obj["link"] = txt
            found_link = True
        if not found_price and isinstance(n, NavigableString):
            if len(categories) == 1 and categories[0] == Item.TOILET_PAPER:
                if " rl." in n.get_text(strip=True):
                    t = n.get_text(strip=True)
                    rolls = float(int(re.sub(r'[^\d]', "", t[:t.index("rl.")])))
                    p1 = node.find(name="span", attrs={"class":"nem-price-container__price-integer"})
                    p2 = node.find(name="sup", attrs={"class":"nem-price-container__price-float"})
                    price = float(p1.get_text(strip=True)+"."+p2.get_text(strip=True))
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
                    obj["price"] = float(re.sub(r'[^\d,]', "", n.get_text(strip=True)).replace(",", "."))
                    obj["unit"] = unit
                    found_price = True
        if not found_name and hasattr(n, "get") and n.get("class") == ["product-card__title", "ng-star-inserted"]:
            name = n.get_text(strip=True).lower()
            if name_include_description:
                next_sibling = n.find_next_sibling()
                if next_sibling:
                    description_text = next_sibling.get_text(strip=True)
                    if description_text:
                        name += " " + description_text.lower()
            obj["original_name"] = name
            found_name = True
        if found_name and found_link and found_price:
            break
    if found_name and found_link and found_price:
        return obj
    return None

def accept_cookies(page):
    page.get_by_role("button", name="OK TIL ALLE").click()
    page.wait_for_load_state("networkidle", timeout=5000)

def get_items_base(url, categories, name_include_description, use_cache = True, cache_time = None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    page = BaseScraper(url, scrolling=True, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    nodes1 = soup.find_all(name="ul", attrs={"class": "nem-one-row__content-items nem-one-row__content-items--products"})
    nodes2 = soup.find_all(name="div", attrs={"class": "nem-show-all__content nem-show-all__content--products"})
    nodes = list(nodes1)+list(nodes2)
    items = []
    for node in nodes:
        for child in node.children:
            if hasattr(child, "descendants"):
                item = parse_item(child, categories, name_include_description)
                if item:
                    items.append(item)
    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://www.nemlig.com/dagligvarer/koed",[Category.MEAT_AND_FISH],False),
        ("https://www.nemlig.com/dagligvarer/frugt-groent/frugt",util_category_fruits,False),
        ("https://www.nemlig.com/dagligvarer/frugt-groent/groentsager",util_category_vegetables,False),
        ("https://www.nemlig.com/dagligvarer/mejeri/maelk-floede",[Item.MILK],False),
        ("https://www.nemlig.com/dagligvarer/mejeri/ost",[Item.CHEESE],False),
        ("https://www.nemlig.com/dagligvarer/mejeri/smoer-fedtstof/smoer",[Item.BUTTER],False),
        ("https://www.nemlig.com/dagligvarer/mejeri/aeg-gaer",[Item.EGG],False),
        ("https://www.nemlig.com/dagligvarer/broed-kiks-og-kager/lyst-groftbroed/hele-broed",[Item.BREAD],False),
        ("https://www.nemlig.com/dagligvarer/nye-varer-inspiration/glutenfri-produkter/broed-kiks-kager",[Item.GLUTEN_FREE_BREAD],True),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/vand",[Item.WATER],False),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/sodavand/cola",[Item.COKE],False),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/sports-energidrikke",[Item.ENERGY_DRINK],False),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/oel/pilsner-lager",[Item.BEER],False),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/oel/lyse-ales",[Item.BEER],False),
        ("https://www.nemlig.com/dagligvarer/drikkevarer/oel/porter-stout",[Item.BEER],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/bagning/hvedemel",[Item.FLOUR],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/bagning/sukker-soedemiddel",[Item.SUGAR],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/krydderier-fond/salt",[Item.SALT],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/olie-eddike/olivenolie",[Item.OLIVE_OIL],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/olie-eddike/raps-solsikke",[Item.SUNFLOWER_OIL],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/pasta-ris-baelgfrugter/ris",[Item.RICE],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/pasta-ris-baelgfrugter/pasta",[Item.SPAGHETTI_PASTA],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/pasta-ris-baelgfrugter/boenner",[Item.RED_BEANS_CAN],False),
        ("https://www.nemlig.com/dagligvarer/kolonial/konserves/groentkonserves",[Item.CRUMBLED_SWEET_CORN_CAN],False),
        ("https://www.nemlig.com/dagligvarer/pleje/haarpleje/shampoo",[Item.SHAMPOO],False),
        ("https://www.nemlig.com/dagligvarer/pleje/hygiejne/haandsaebe",[Item.SOAP],False),
        ("https://www.nemlig.com/dagligvarer/pleje/tandpleje/tandpasta",[Item.TOOTHPASTE],False),
        ("https://www.nemlig.com/dagligvarer/pleje/hygiejne/bind-tamponer",[Item.TAMPON],False),
        ("https://www.nemlig.com/dagligvarer/pleje/toiletartikler/sex-samliv",[Item.CONDOM],False),
        ("https://www.nemlig.com/dagligvarer/husholdning/toiletpapir-koekkenrulle/toiletpapir",[Item.TOILET_PAPER],True),
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