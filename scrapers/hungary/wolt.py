import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "wolt.com"
LISTING_URL = "https://wolt.com/en/search?q=a&target=venues&filters=product_line%3Drestaurant%26category%3Dafrican%252Camerican%252Carabic%252Casian%252Caustrian%252Cbbq%252Cbowl%252Cbreakfast%252Cbrunch%252Cburgers%252Cchicken%252Cchinese%252Ccaucasian%252Ccurry%252Cdoner%252Ceuropean%252Cfalafel%252Cgerman%252Cgluten-free%252Cgyros%252Chealthy%252Chungarian%252Cindian%252Citalian%252Cinternational%252Cjapanese%252Ckebab%252Ckorean%252Clunch%252Cmexican%252Cmediterranean%252Cnoodles%252Cpasta%252Cpizza%252Cramen%252Crussian%252Csandwich%252Csteak%252Cstreet_food%252Csushi%252Ctapas%252Cthai%252Cturkish%252Cudon%252Cvegan%252Cvegetarian%252Cvietnamese"

# Section headings that are NOT main courses — exclude them.
# Covers: drinks, desserts, starters, soups, promo/deal banners, sides, breakfast pastries.
SECTION_EXCLUDE = [
    # drinks
    "ital", "drink", "beverage", "kávé", "coffee", "tea", "smoothie", "juice",
    "lemonade", "limonádé", "sör", "beer", "bor", "wine", "koktél", "cocktail",
    "üdítő",
    # desserts / sweets / pastry
    "desszert", "dessert", "sütemény", "cake", "fánk", "donut", "piskóta",
    "croissant", "waffle", "gofri", "fagylalt", "ice cream", "torta",
    "kenyér",
    # starters / soups
    "előétel", "starter", "leves", "soup",
    # sides / extras / sauces
    "köret", "side", "szósz", "sauce", "dip", "feltét", "topping", "extra",
    "add-on", "addon", "kiegészítő", "savanyúság",
    # promo / deal / seasonal banners
    "ajánlat", "offer", "deal", "promo", "promoci", "akció", "wolt+",
    "coca-cola", "sprite", "pepsi", "combo", "kiemelt", "szezonális", "seasonal",
    "újdonság", "new", "highlight", "bundle", "ajándékutalvány",
    # aggregation / navigation sections (not real menu sections)
    "most ordered",
]

PRICE_MIN = 800.0
PRICE_MAX = 15000.0

def get_restaurant_links(use_cache=True, cache_time=None):
    cache = retrieve_cache(LISTING_URL[:100], use_cache, cache_time)
    if cache is not None:
        return list(cache["link"].dropna().unique())
    page = BaseScraper(LISTING_URL, scrolling=True).get_page()
    soup = BeautifulSoup(page, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/en/hun/budapest/restaurant/" in href and href not in links:
            links.append(href)
    df = pd.DataFrame({"link": links})
    save_cache(LISTING_URL[:100], df)
    return links

def scrape_restaurant(url, use_cache=True, cache_time=None):
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    page = BaseScraper(url, scrolling=True).get_page()
    soup = BeautifulSoup(page, "lxml")
    vendor_name = soup.find("span", attrs={"data-test-id":"venue-hero.venue-title"}).get_text(strip=True).lower()
    items = []
    for sec in soup.find_all("div", attrs={"data-test-id":"MenuSection"}):
        cat = sec.find("h2").get_text(strip=True).lower()
        if any(k in cat for k in SECTION_EXCLUDE):
            continue
        for name_tag in sec.find_all("h3", attrs={"data-test-id":"horizontal-item-card-header"}):
            price_tag = name_tag.find_next("span", attrs={"data-test-id":"horizontal-item-card-price"})
            if not price_tag:
                continue
            m = re.search(r"([\d\s,]+)", price_tag.get_text(strip=True))
            if not m:
                continue
            price = float(re.sub(r"[\s,]", "", m.group(1)))
            if not (PRICE_MIN <= price <= PRICE_MAX):
                continue
            item = {
                "price": price,
                "unit": Unit.EACH,
                "country": Country.HU,
                "language": Lang.EN,
                "currency": Currency.HUF,
                "vendor": VENDOR,
                "link": url,
                "categories": [Item.EATING_OUT],
                "original_name": "%s - %s - %s" % (vendor_name, cat, name_tag.get_text(strip=True).lower()),
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
    for slug in links:
        url = "https://wolt.com" + slug
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
