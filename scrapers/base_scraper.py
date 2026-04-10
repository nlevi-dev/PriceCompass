import time
import requests
from pathlib import Path
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

DEFAULT_CACHE_TIME = 20

class BaseScraper:
    def __init__(
        self,
        url,
        scrolling = False,
        post_init_action = None,
        post_scroll_action = None,
    ):
        self.url = url
        self.scrolling = scrolling
        self.post_init_action = post_init_action
        self.post_scroll_action = post_scroll_action
        self.cache_dir = Path(__file__).resolve().parent.parent/"cache"
        self.cache_dir.mkdir(exist_ok=True)

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
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1080, 'height': 720},
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
