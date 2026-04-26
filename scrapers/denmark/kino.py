import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re

import pandas as pd
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, retrieve_cache, save_cache
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df

VENDOR = "kino.dk"
LISTING_URL = "https://www.kino.dk/ticketflow/showtimes?sort=popularity"

def accept_cookies_1(page):
    page.get_by_role("button", name="Tillad alle cookies").click()
    page.wait_for_timeout(20000)

def get_movie_links(use_cache=True, cache_time=None):
    cache = retrieve_cache(LISTING_URL, use_cache, cache_time)
    if cache is not None:
        return list(cache["link"].dropna().unique())
    page = BaseScraper(LISTING_URL, scrolling=True, post_init_action=accept_cookies_1, user_agent=None, headless=True).get_page()
    soup = BeautifulSoup(page, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/ticketflow/showtimes?movies" in href:
            full = href if href.startswith("http") else "https://www.kino.dk" + href
            full += "&city=52-21-80-7-82-16-2-87-83-92-56-76-54-71"
            if full not in links:
                links.append(full)
    df = pd.DataFrame({"link": links})
    save_cache(LISTING_URL, df)
    return links

def accept_cookies_2(page):
    page.get_by_role("button", name="Tillad alle cookies").click()
    page.wait_for_timeout(60000)

def scout_movie(url, use_cache=True, cache_time=None):
    cache = retrieve_cache(url+"_subvendors", use_cache, cache_time)
    if cache is not None:
        return list(cache["vendors"].dropna().unique())
    page = BaseScraper(url, scrolling=False, post_init_action=accept_cookies_2, user_agent=None, headless=True).get_page()
    soup = BeautifulSoup(page, "lxml")
    subs = soup.find_all("div", class_="movie-showtimes__cinemas")
    subs = [s.find("h4").get_text(strip=True) for s in subs]
    df = pd.DataFrame({"vendors": subs})
    save_cache(url+"_subvendors", df)
    return df

def navigate_movie(SUB):
    def navigate_movie(page):
        page.get_by_role("button", name="Tillad alle cookies").click()
        page.wait_for_timeout(60000)
        for cinema in page.locator("div.movie-showtimes__cinemas").all():
            if re.sub(r"\s","",cinema.locator("h4").inner_text().strip()) == SUB:
                slot = cinema.locator("div.date-picker__hall-time.date-picker__hall-time--available").first
                slot.dispatch_event("click")
                break
        page.wait_for_timeout(60000)
        if SUB in ["BIGBIONordhavn,København","ValbyKino,København"]:
            frame = next(f for f in page.frames if f.locator("body#MasterPageBodyTag").count() > 0)
            frame.locator("body").wait_for()
            frame.locator('select[name="antal"]').select_option("1")
            page.wait_for_timeout(60000)
            price = frame.locator("div.footerBar").first.locator("div.col-xs-6.hidden-sm.hidden-md.hidden-lg.text-center.idfooterinfo").first.inner_text().strip()
            page.evaluate(f"document.body.innerHTML += '<div id=\\'__PRICE_IFRAME_SCRAPED__\\'>{price}</div>'")
        elif SUB in ["EmpireBio,København"]:
            pass
        else:
            raise Exception("Should not happen!")
    return navigate_movie

def scrape_movie(url, sub, use_cache=True, cache_time=None):
    sub = re.sub(r"\s","",sub)
    if sub not in ["ValbyKino,København","EmpireBio,København"]:
        return pd.DataFrame()
    cache = retrieve_cache(url, use_cache, cache_time)
    if cache is not None:
        return cache
    items = []
    page = BaseScraper(url, scrolling=False, post_init_action=navigate_movie(sub), user_agent=None, headless=False).get_page()
    df = pd.DataFrame(items)
    # save_cache(url, df)
    return df

def get_items(use_cache=True, cache_time=None):
    links = get_movie_links(use_cache=use_cache, cache_time=cache_time)
    if len(links) > 15:
        links = links[:15]
    dfs = []
    for url in links:
        subs = scout_movie(url, use_cache=use_cache, cache_time=cache_time)
        for sub in subs:
            try:
                df = scrape_movie(url, sub, use_cache=use_cache, cache_time=cache_time)
                if len(df) > 0:
                    dfs.append(df)
            except Exception as e:
                print("Error scraping %s - %s: %s" % (url, sub, e))
    df = pd.concat(dfs, ignore_index=True)
    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df = df.drop_duplicates("original_name", keep="first", ignore_index=True)
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
