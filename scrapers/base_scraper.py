import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import time
import requests
from pathlib import Path
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from scrapers.items import read_csv_raw

DEFAULT_CACHE_TIME = 20

root_path = Path(__file__).resolve().parent.parent

def string_to_cache_name(txt):
    txt = re.sub(r'[^a-zA-Z0-9]', "", txt)
    txt = txt.replace("https","")
    txt = txt.replace("http","")
    txt = txt.replace("www","")
    return txt+".csv"

def retrieve_cache(url, use_cache = True, cache_time = None):
    cache_name = string_to_cache_name(url)
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            try:
                ret = read_csv_raw(cache_path)
                return ret
            except:
                return None
    return None

def save_cache(url, df):
    cache_name = string_to_cache_name(url)
    cache_path = root_path / "cache" / cache_name
    df.to_csv(cache_path, index=False)

class BaseScraper:
    def __init__(
        self,
        url,
        scrolling = False,
        post_init_action = None,
        post_scroll_action = None,
        headless = True,
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ):
        self.url = url
        self.scrolling = scrolling
        self.post_init_action = post_init_action
        self.post_scroll_action = post_scroll_action
        self.cache_dir = Path(__file__).resolve().parent.parent/"cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.user_agent = user_agent

    def is_allowed_by_robots(self):
        parsed_url = urlparse(self.url)
        netloc = parsed_url.netloc
        robots_url = f"{parsed_url.scheme}://{netloc}/robots.txt"
        cache_path = self.cache_dir / (netloc.replace(".", "_") + ".txt")
        
        rp = RobotFileParser()

        use_cache = False
        if cache_path.exists():
            file_age = time.time() - cache_path.stat().st_mtime
            if file_age < 3600:
                use_cache = True

        if use_cache:
            with open(cache_path, "r", encoding="utf-8") as f:
                rp.parse(f.read().splitlines())
        else:
            content = ""
            try:
                response = requests.get(robots_url, timeout=30)
                if response.status_code == 200:
                    content = response.text
            except:
                pass
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(content)
            rp.parse(content.splitlines())
                    
        return rp.can_fetch("PriceCompassBot", self.url)
    
    def get_viewport_fingerprint(self, page):
        return page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                let visibleText = "";
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    ) {
                        visibleText += el.innerText;
                    }
                }
                return visibleText;
            }
        """)
    
    def get_page(self):
        if not self.is_allowed_by_robots():
           raise Exception(f"Scraping \"{self.url}\" is not allowed by robots.txt!")
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=self.headless)
            additional_props = {}
            if self.user_agent is not None:
                additional_props["user_agent"] = self.user_agent
            context = browser.new_context(
                viewport={'width': 1080, 'height': 720},
                **additional_props
            )
            page = context.new_page()

            page.goto(self.url, timeout=60000)

            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass

            if self.post_init_action is not None:
                try:
                    self.post_init_action(page)
                except:
                    pass
            
            if self.scrolling:
                cnt_min = 3
                cnt_max = 100
                cnt = 0
                last_fingerprint = ""
                while True:
                    current_fingerprint = self.get_viewport_fingerprint(page)

                    if cnt > cnt_max or (cnt > cnt_min and current_fingerprint == last_fingerprint):
                        break

                    last_fingerprint = current_fingerprint
                    cnt += 1
                    
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(500)

                    if self.post_scroll_action is not None:
                        try:
                            self.post_scroll_action(page)
                        except:
                            pass

            page.wait_for_timeout(1000)

            current_html = page.content()
            browser.close()
            return current_html
