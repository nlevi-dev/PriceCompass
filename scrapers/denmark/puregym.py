import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "puregym.dk"
URL = "https://www.puregym.dk/priser"

def accept_cookies(page):
    try:
        page.get_by_role("button", name="Accepter alle").click()
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        pass

def get_items(use_cache=True, cache_time=None):
    cache = retrieve_cache(URL, use_cache, cache_time)
    if cache is not None:
        return raw_items_to_df(cache)

    page = BaseScraper(URL, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")

    items = []

    # Monthly memberships: Unlimited, Plus, Core
    for node in soup.find_all("div", class_="grid-disclosure__item"):
        suffix = node.find("p", class_="grid-disclosure__head__suffix__title")
        if not suffix:
            continue
        m = re.search(r'(\d+)\s*kr\./md\.', suffix.get_text(strip=True))
        if not m:
            continue
        price = float(m.group(1))
        # first direct child text node is the tier name (Unlimited / Plus / Core)
        head = node.find(class_="grid-disclosure__head__title")
        tier = head.get_text(strip=True).lower() if head else ""
        if not tier:
            continue
        items.append({
            "price": price,
            "unit": Unit.MONTHLY,
            "country": Country.DK,
            "language": Lang.DK,
            "currency": Currency.DKK,
            "vendor": VENDOR,
            "link": URL,
            "categories": [Item.GYM_MONTHLY_MEMBERSHIP],
            "original_name": f"puregym månedlig {tier}",
        })

    # Prepaid: parse all durations from the prepaid strong node
    prepaid_map = [
        (r'1\s*dag\sfra\s*([\d\.]+),-', Unit.EACH, [Item.GYM_SINGLE_ENTRANCE], "puregym dagskort forudbetalt"),
        (r'1\s*md\.\s*fra\s*([\d\.]+),-', Unit.MONTHLY, [Item.GYM_MONTHLY_MEMBERSHIP], "puregym månedlig forudbetalt"),
        (r'12\s*mdr\.\s*fra\s*([\d\.]+),-', Unit.YEARLY,  [Item.GYM_YEARLY_MEMBERSHIP], "puregym årlig forudbetalt"),
    ]
    for node in soup.find_all("strong"):
        text = node.get_text(strip=True)
        for pattern, unit, categories, name in prepaid_map:
            m = re.search(pattern, text)
            if m:
                items.append({
                    "price": float(m.group(1).replace(".", "")),
                    "unit": unit,
                    "country": Country.DK,
                    "language": Lang.DK,
                    "currency": Currency.DKK,
                    "vendor": VENDOR,
                    "link": URL,
                    "categories": categories,
                    "original_name": name,
                })
        if re.search(r'12\s*mdr\.', text):
            break

    df = pd.DataFrame(items)
    save_cache(URL, df)

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
