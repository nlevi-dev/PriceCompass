import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re
import time

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, DEFAULT_CACHE_TIME
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df, read_csv_raw

root_path = Path(__file__).resolve().parent.parent.parent

VENDOR = "vesterbronxgym.dk"
URL = "https://vesterbronxgym.dk/vesterbronx-gym-2/"

def accept_cookies(page):
    try:
        page.get_by_role("button", name="Accepter alle").click()
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        pass

def get_items(use_cache=True, cache_time=None):
    cache_name = re.sub(r'[^a-zA-Z0-9]', "", URL) + ".csv"
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            df = read_csv_raw(cache_path)
            return raw_items_to_df(df)

    page = BaseScraper(URL, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")

    items = []
    for node in soup.find_all(class_="elementor-price-table"):
        heading = node.find(class_="elementor-price-table__heading")
        period = node.find(class_="elementor-price-table__period")
        price_node = node.find(class_="elementor-price-table__integer-part")
        if not heading or not period or not price_node:
            continue
        heading_text = heading.get_text(strip=True).lower()
        period_text = period.get_text(strip=True).lower()
        price = float(price_node.get_text(strip=True))

        if period_text == "pr. måned" and "personlig" not in heading_text and "junior" not in heading_text:
            unit = Unit.MONTHLY
            categories = [Item.GYM_MONTHLY_MEMBERSHIP]
            name = f"vesterbronx medlemskab {heading_text}"
        elif period_text == "pr. dag" and "day pass" in heading_text:
            unit = Unit.EACH
            categories = [Item.GYM_SINGLE_ENTRANCE]
            name = f"vesterbronx day pass"
        else:
            continue

        items.append({
            "price": price,
            "unit": unit,
            "country": Country.DK,
            "language": Lang.DK,
            "currency": Currency.DKK,
            "vendor": VENDOR,
            "link": URL,
            "categories": categories,
            "original_name": name,
        })

    df = pd.DataFrame(items)
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)

    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df = raw_items_to_df(df)
    df = df.drop_duplicates(["name", "price", "unit"], keep="first", ignore_index=True)
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
    print(get_items(use_cache=(not args.no_cache), cache_time=args.cache_time))
