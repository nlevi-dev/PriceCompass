import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import copy

import pandas as pd

from scrapers.types import *
from scrapers.exchange import CurrencyExchanger

exchanger = CurrencyExchanger()

def filter_lookup(lookup, categories):
    items = [c for c in categories if isinstance(c, Item)]
    categories = [c for c in categories if isinstance(c, Category)]
    lookup = copy.deepcopy(lookup)
    lookup_filtered = {}
    for item in lookup:
        if lookup[item][Category.NONE] in categories:
            lookup_filtered[item] = lookup[item]
    for item in items:
        lookup_filtered[item] = lookup[item]
    return lookup_filtered

def raw_items_to_df(items):
    items.insert(0, "name", "")
    items.insert(4, "category", "")
    indices = []
    for idx, item in items.iterrows():
        lookup = filter_lookup(lookup_filters, item["categories"])

        # exchange currency to EUR
        if item["currency"] != Currency.EUR:
            items.at[idx, "price"] = item["price"] * exchanger.get_exchange_rate(item["currency"], Currency.EUR)
        
        units = {key:lookup[key][Unit.NONE] for key in lookup}
        categories = {key:lookup[key][Category.NONE] for key in lookup}
        lookup = {key:lookup[key][item["language"]] for key in lookup}
        
        for schema in lookup:

            unit = units[schema]
            category = categories[schema]

            # check blacklist
            blacklist = lookup[schema][1]
            skip = False
            for black in blacklist:
                if black in item["original_name"]:
                    skip = True
                    break
            if skip:
                continue

            # check whitelist
            whitelist = lookup[schema][0]
            if len(whitelist) == 1 and len(whitelist[0]) == 0:
                continue
            for white in whitelist:
                found = True
                for part in white:
                    if part not in item["original_name"]:
                        found = False
                        break
                if found and item["unit"] == unit:
                    items.at[idx, "name"] = schema
                    items.at[idx, "category"] = category
                    indices.append(idx)
                    break
    df = items.iloc[indices].reset_index(drop=True)
    df.drop(columns=["currency","language","categories"], inplace=True)
    for col in ["vendor", "link", "original_name"]:
        df[col] = df[col].str.replace("\n", " ", regex=False)
    return df

ENUM_COLS = ["name", "unit", "country", "category"]
def read_csv(path):
    df = pd.read_csv(path)
    df[ENUM_COLS] = df[ENUM_COLS].map(parse_enum)
    return df

ENUM_COLS_RAW = ["unit", "country", "language", "currency"]
def read_csv_raw(path):
    df = pd.read_csv(path)
    cols = list(set(ENUM_COLS_RAW).intersection(set(df.columns)))
    if len(cols) > 0:
        df[cols] = df[cols].map(parse_enum)
    if "categories" in df.columns:
        df["categories"] = df["categories"].apply(lambda x: [parse_enum(c[:c.rfind(":")]) for c in re.sub(r'[\<\>\[\]]', "", x).split(", ")])
    return df