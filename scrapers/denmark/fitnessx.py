import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re
import json
import html

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "fitnessx.dk"
URL_PRISER = "https://fitnessx.dk/oevrige-priser/"
URL_TILMELDING = "https://fitnessx.dk/tilmelding/"

# Copenhagen centre UUIDs from data-ref on the city button
CPH_UUIDS = {
    "7a48160e-4eeb-4071-a7f6-22a6c2767df1",
    "867170b0-fb40-42ae-b28b-0388f74ca902",
    "a649489c-477b-498c-98c2-24ee077bd1cc",
    "f8d9325b-399f-4a83-bb92-543dfe97f4f0",
}

def accept_cookies(page):
    try:
        page.get_by_role("button", name="Accepter alle").click()
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        pass

def base_item(price, unit, name, categories, url):
    return {
        "price": price,
        "unit": unit,
        "country": Country.DK,
        "language": Lang.DK,
        "currency": Currency.DKK,
        "vendor": VENDOR,
        "link": url,
        "categories": categories,
        "original_name": name,
    }

def get_items(use_cache=True, cache_time=None):
    cache = retrieve_cache(VENDOR, use_cache, cache_time)
    if cache is not None:
        return raw_items_to_df(cache)

    items = []

    # --- Day pass from oevrige-priser ---
    page_priser = BaseScraper(URL_PRISER, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page_priser, "lxml")
    headings = [n.get_text(strip=True) for n in soup.find_all("span", class_="elementor-heading-title")]
    for i, text in enumerate(headings):
        if "day pass" in text.lower():
            if i + 1 < len(headings):
                m = re.search(r'(\d+)', headings[i + 1])
                if m:
                    items.append(base_item(float(m.group(1)), Unit.EACH, "fitnessx dagspas", [Item.GYM_SINGLE_ENTRANCE], URL_PRISER))
            break

    # --- Monthly memberships from tilmelding JS object ---
    page_tilmelding = BaseScraper(URL_TILMELDING, scrolling=False, post_init_action=accept_cookies).get_page()
    m = re.search(r'var sj_ajax_object = ({.*?});', page_tilmelding, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        for membership in data.get("medlemskaber", []):
            acf = membership["acf"]
            centres = set(acf.get("centre") or [])
            if not centres.intersection(CPH_UUIDS):
                continue
            title = html.unescape(membership["title"])
            if any(x in title.lower() for x in ["træningsven", "åbningstilbud", "umeus"]):
                continue
            pris = acf.get("pris")
            if not pris:
                continue
            price = float(str(pris).replace(",", "."))
            name = f"fitnessx månedlig {title.lower()}"
            items.append(base_item(price, Unit.MONTHLY, name, [Item.GYM_MONTHLY_MEMBERSHIP], URL_TILMELDING))

    df = pd.DataFrame(items)
    save_cache(VENDOR, df)

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
