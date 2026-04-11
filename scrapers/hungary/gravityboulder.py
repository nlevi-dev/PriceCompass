import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import re
import time
import requests

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import pandas as pd
import pytesseract
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, DEFAULT_CACHE_TIME
from scrapers.items import Item, Unit, Country, Lang, Currency, raw_items_to_df, read_csv_raw

root_path = Path(__file__).resolve().parent.parent.parent

VENDOR = "gravitybudapest.com"

def extract_table_with_headers(numpy_image):
    if len(numpy_image.shape) == 3:
        gray = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2GRAY)
    else:
        gray = numpy_image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    d = pytesseract.image_to_data(gray, lang="hun", output_type=pytesseract.Output.DICT)
    df = pd.DataFrame(d)
    df = df[df['text'].str.strip() != ""]
    
    # Find header keywords
    keywords = ['felnőtt', 'diák', 'gyerek']
    header_matches = []
    
    for keyword in keywords:
        matches = df[df['text'].str.lower().str.contains(keyword, na=False)]
        if not matches.empty:
            # Get the topmost match for this keyword
            topmost = matches.loc[matches['top'].idxmin()]
            header_matches.append({
                'keyword': keyword,
                'left': topmost['left'],
                'top': topmost['top'],
                'width': topmost['width'],
                'height': topmost['height'],
                'center_x': topmost['left'] + topmost['width'] / 2
            })
    
    if len(header_matches) != 3:
        return pd.DataFrame()
    
    # Sort headers by x position (left to right)
    header_matches.sort(key=lambda x: x['left'])
    
    # Find the topmost header position
    min_header_top = min(header['top'] for header in header_matches)
    
    # Get all words below the headers
    words_below = df[df['top'] > min_header_top + max(header['height'] for header in header_matches)]
    
    # Group words into columns based on header positions
    result_data = []
    
    # Group words by rows (similar y positions)
    row_groups = {}
    tolerance = 10  # pixels tolerance for grouping words in same row
    
    for _, word in words_below.iterrows():
        word_center_y = word['top'] + word['height'] / 2
        
        # Find existing row group or create new one
        found_group = False
        for group_y in row_groups:
            if abs(word_center_y - group_y) <= tolerance:
                row_groups[group_y].append(word)
                found_group = True
                break
        
        if not found_group:
            row_groups[word_center_y] = [word]
    
    # Process each row group
    for row_y in sorted(row_groups.keys()):
        row_words = row_groups[row_y]
        
        # Initialize row data: [row_label, col1_data, col2_data, col3_data]
        row_data = ['', '', '', '']
        
        for word in row_words:
            word_center_x = word['left'] + word['width'] / 2
            
            # Check if word belongs to any header column
            assigned_to_header = False
            for i, header in enumerate(header_matches):
                header_left = header['left']
                header_right = header['left'] + header['width']
                if header_left <= word_center_x and word_center_x <= header_right + (header['width'] if header['keyword'] == 'diák' else 0):
                    if row_data[i + 1]:  # If already has data, append with space
                        row_data[i + 1] += ' ' + word['text']
                    else:
                        row_data[i + 1] = word['text']
                    assigned_to_header = True
                    break
            
            # If not assigned to any header column, it's row label data
            if not assigned_to_header:
                if row_data[0]:  # If already has data, append with space
                    row_data[0] += ' ' + word['text']
                else:
                    row_data[0] = word['text']
        
        # Only add row if it has some data
        if any(cell.strip() for cell in row_data):
            result_data.append(row_data)
    
    # Create DataFrame with appropriate column names
    columns = ['row_data'] + [header['keyword'] for header in header_matches]
    return pd.DataFrame(result_data, columns=columns)

def accept_cookies(page):
    page.get_by_role("button", name="Ok").click()
    page.wait_for_load_state("networkidle", timeout=5000)

unit_lookup = {
    Unit.EACH: ["belépő (korlátlan)"],
    Unit.MONTHLY: ["1 hónap"],
    Unit.YEARLY: ["12 hónap"],
}

def get_items_base(url, categories, place, use_cache = True, cache_time = None):
    cache_name = re.sub(r'[^a-zA-Z0-9]', "", url)+".csv"
    cache_path = root_path / "cache" / cache_name
    if cache_time is None:
        cache_time = DEFAULT_CACHE_TIME
    if use_cache and cache_path.exists():
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age < cache_time * 3600:
            df = read_csv_raw(cache_path)
            return df
    page = BaseScraper(url, scrolling=False, post_init_action=accept_cookies).get_page()
    soup = BeautifulSoup(page, "lxml")
    node = soup.find(name="img", attrs={"class":"aligncenter size-full wp-image-3801"})

    df = pd.DataFrame()
    if node and node.get('src'):
        img_url = node.get('src')
        if img_url.startswith('/'):
            img_url = 'https://gravitybudapest.com' + img_url
        response = requests.get(img_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            df = extract_table_with_headers(np.array(img))

            header_indices = []
            headers = []
            for idx, row in df.iterrows():
                row_data = str(row['row_data']).strip()
                if not row_data or row_data == 'nan':
                    continue
                cleaned_text = re.sub(r'\([^)]*\)', '', row_data)
                alphanumeric_only = re.sub(r'[^a-zA-Z0-9]', '', cleaned_text)
                if len(alphanumeric_only) == 0:
                    continue
                uppercase_count = sum(1 for c in alphanumeric_only if c.isupper())
                uppercase_ratio = uppercase_count / len(alphanumeric_only)
                if uppercase_ratio >= 0.9:
                    header_indices.append(idx)
                    headers.append(re.sub(r'[^a-zA-Z0-9öÖüÜóÓúÚőŐáÁűŰéÉíÍ ]', '', cleaned_text).lower().strip())
            if not header_indices:
                return []
            groups = {}
            for i, header_idx in enumerate(header_indices):
                if i + 1 < len(header_indices):
                    end_idx = header_indices[i + 1]
                else:
                    end_idx = len(df)
                group_df = df.iloc[header_idx+1:end_idx].copy()
                groups[headers[i]] = group_df
            
            obj = {
                "price": None,
                "unit": None,
                "country": Country.HU,
                "language": Lang.HU,
                "currency": Currency.HUF,
                "vendor": VENDOR,
                "link": url,
                "categories": categories,
                "original_name": "",
            }
            items = []
            for cat in groups:
                group = groups[cat]
                group = group[group["felnőtt"].astype(str).str.contains(r'\d', na=False)]
                for _, row in group.iterrows():
                    item = obj.copy()
                    item["original_name"] = place+cat+" "+str(row["row_data"]).strip().lower()
                    item["price"] = float(int(re.sub(r'\D', '', str(row["felnőtt"]))))
                    unit = None
                    for u in unit_lookup:
                        for unit_text in unit_lookup[u]:
                            if unit_text in item["original_name"]:
                                unit = u
                                break
                    if unit is not None:
                        item["unit"] = unit
                        items.append(item)
            df = pd.DataFrame(items)
    
    cache_path.parent.mkdir(exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df

def get_items(use_cache = True, cache_time = None):
    urls = [
        ("https://gravitybudapest.com/araink/",[Item.CLIMBING_GYM_SINGLE_ENTRANCE,Item.CLIMBING_GYM_MONTHLY_MEMBERSHIP,Item.CLIMBING_GYM_YEARLY_MEMBERSHIP],"gravityboulder "),
    ]
    dfs = []
    for url, categories, place in urls:
        dfs.append(get_items_base(url, categories, place, use_cache=use_cache, cache_time=cache_time))
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates("original_name", keep="first", ignore_index=True)
    if len(df) == 0:
        raise Exception(f"No items from {VENDOR}!")
    df = raw_items_to_df(df)
    df = df.drop_duplicates(["name","price","unit"], keep="first", ignore_index=True)
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