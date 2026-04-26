import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "just-eat.dk"
LISTING_URL = "https://www.just-eat.dk/en/delivery/food/koebenhavn-k-1304"

# Exclude section headings that are clearly not main-course food sections.
# Everything else is treated as a potential main dish section.
SECTION_EXCLUDE = [
    "drink", "beverage", "beer", "wine", "ros", "soda", "water", "juice",
    "dessert", "snack", "side", "sauce", "dip", "bread", "naan", "roti",
    "starter", "soup", "salad", "kids", "children", "add-on", "addon",
    "extra", "shot", "shake", "coffee", "tea", "hot drink", "cold drink",
    "highlight", "basket", "business", "accessori", "small dish",
    "bundle", "deal", "offer", "combo", "menus",
    "biryani", "nigiri", "sashimi", "yakitori", "roll",
    "thali", "bobler", "vand", "drikke", "smoothie",
    "kombucha", "cutlery", "napkin", "pose", "gift", "service",
    "happy meal", "king jr", "jr. meal",
    "slice", "addition", "kcal life",
]
# Price bounds to filter out sides/sauces (too cheap) and multi-person set menus (too expensive)
PRICE_MIN = 50.0
PRICE_MAX = 500.0

def get_restaurant_links(use_cache=True, cache_time=None):
    cache = retrieve_cache(LISTING_URL, use_cache, cache_time)
    if cache is not None:
        return list(cache["link"].dropna().unique())
    page = BaseScraper(LISTING_URL, scrolling=True, user_agent=None).get_page()
    soup = BeautifulSoup(page, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/en/menu/" in href:
            full = href if href.startswith("http") else "https://www.just-eat.dk" + href
            if full not in links:
                links.append(full)
    df = pd.DataFrame({"link": links})
    save_cache(LISTING_URL, df)
    return links

def scrape_restaurant(url, use_cache=True, cache_time=None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    page = BaseScraper(url, scrolling=True, user_agent=None).get_page()
    soup = BeautifulSoup(page, "lxml")
    vendor_name = soup.find("h1", attrs={"data-qa":"heading"}).get_text(strip=True).lower()
    items = []
    for sec in soup.find_all("section", class_="item-category-style_section__XhoNI"):
        cat = sec.find("h2", attrs={"data-qa":"heading"}).get_text(strip=True).lower()
        if any(k in cat for k in SECTION_EXCLUDE):
            continue
        ul = sec.find("ul", class_="item-list_list-wrapper__31Wbo")
        if not ul:
            continue
        for li in ul.find_all("li", recursive=False):
            name_node = li.find(attrs={"data-qa": "item-name"})
            price_node = li.find(attrs={"data-qa": "item-price"})
            if not name_node or not price_node:
                continue
            m = re.search(r"([\d]+[,.][\d]+)", price_node.get_text(strip=True))
            if not m:
                continue
            price = float(m.group(1).replace(",", "."))
            if not (PRICE_MIN <= price <= PRICE_MAX):
                continue
            item ={
                "price": price,
                "unit": Unit.EACH,
                "country": Country.DK,
                "language": Lang.DK,
                "currency": Currency.DKK,
                "vendor": VENDOR,
                "link": url,
                "categories": [Item.EATING_OUT],
                "original_name": "%s - %s - %s" % (vendor_name, cat, name_node.get_text(strip=True).lower()),
            }
            items.append(item.copy())
            item["categories"] = [Item.FAST_FOOD]
            items.append(item.copy())
    df = pd.DataFrame(items)
    save_cache(url, df)
    return df

def get_items(use_cache=True, cache_time=None):
    links = get_restaurant_links(use_cache=use_cache, cache_time=cache_time)
    if len(links) > 100:
        links = links[:100]
    dfs = []
    for url in links:
        try:
            df = scrape_restaurant(url, use_cache=use_cache, cache_time=cache_time)
            if len(df) > 0:
                dfs.append(df)
        except Exception as e:
            print("Error scraping %s: %s" % (url, e))
    df = pd.concat(dfs, ignore_index=True)
    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df["tmp"] = df["categories"].apply(lambda x: str(x))
    df = df.drop_duplicates(["original_name", "tmp"], keep="first", ignore_index=True)
    df = df.drop(columns=["tmp"])
    df = raw_items_to_df(df)
    return df

if __name__ == "__main__":
    import shutil
    import argparse
    terminal_width, _ = shutil.get_terminal_size()
    pd.set_option("display.max_colwidth", terminal_width // 2)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", terminal_width)
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--no_cache", action="store_true", help="")
    parser.add_argument("--cache_time", type=int, required=False, help="")
    args = parser.parse_args()
    print(get_items(use_cache=(not args.no_cache), cache_time=args.cache_time))
