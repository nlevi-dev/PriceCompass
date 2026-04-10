import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import copy
from datetime import datetime

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
    return df

def df_to_data(df: pd.DataFrame, lanuages=[Lang.EN]):
    # {
    #     "date": "2026-03-24",
    #     "translations": {
    #         "EN": {
    #             "data": [
    #                 {
    #                     "category": "Meat and Fish",
    #                     "countries": {
    #                         "Hungary": [
    #                             {
    #                                 "name": "Pork Mince",
    #                                 "unit": "kg",
    #                                 "items": [
    #                                     {
    #                                         "price": 1,
    #                                         "vendor": "auchan.hu",
    #                                         "link": "[LINK]",
    #                                         "name": "daralt hus",
    #                                     }
    #                                 ]
    #                             }
    #                         ]
    #                     },
    #                 }
    #             ],
    #             "countries": ["Hungary"],
    #             "countries_raw": [],
    #             "categories_raw": [],
    #             "items_raw": [],
    #             "aggregate_raw": [],
    #             "exchange": {"Hungary":{"currency":"HUF","value":1}},
    #         }
    #     }
    # }
    data = {}
    data["date"] = datetime.now().strftime('%Y-%m-%d')
    translations = {}
    for lang in lanuages:
        translation = {}
        translation_data = []
        countries = []
        for category in list(Category)[1:]:
            category_data = {}
            df2 = df.copy()
            df2 = df2[df2["category"] == category]
            if len(df2) == 0:
                continue
            df2["country_text"] = df2["country"].apply(lambda x: str(x))
            grp = df2.groupby(by="country_text")
            for country_text, group in grp:
                country = parse_enum(country_text)
                if len(group) == 0:
                    continue
                if country not in countries:
                    countries.append(country)
                country_data = []
                for name in list(Item):
                    df3 = group.copy()
                    df3 = df3[df3["name"] == name]
                    if len(df3) == 0:
                        continue
                    df3 = df3.sort_values(by=["vendor", "price"], ascending=[True, True], na_position="last", axis=0, ignore_index=True)
                    items = []
                    for _, row in df3.iterrows():
                        items.append({
                            "price": row["price"],
                            "vendor": row["vendor"],
                            "link": row["link"],
                            "name": row["original_name"],
                        })
                    country_data.append({"name":enum_to_string(name, lang), "unit":enum_to_string(lookup_filters[name][Unit.NONE], lang), "items":items})
                category_data[enum_to_string(country, lang)] = country_data
            translation_data.append({"category":enum_to_string(category, lang), "countries":category_data})
        translation["data"] = translation_data
        exchange = {}
        for country in countries:
            if country in lookup_currency:
                exchange[enum_to_string(country, lang)] = {"currency":enum_to_string(lookup_currency[country], lang), "value":1.0/exchanger.get_exchange_rate(lookup_currency[country], Currency.EUR)}
        translation["countries"] = sorted([enum_to_string(c, lang) for c in countries])
        translation["countries_raw"] = [enum_to_string(c, lang) for c in list(Country)[1:]]
        translation["categories_raw"] = [enum_to_string(c, lang) for c in list(Category)[1:]]
        translation["items_raw"] = [enum_to_string(c, lang) for c in list(Item)]
        translation["aggregate_raw"] = [enum_to_string(c, lang) for c in list(Aggregate)]
        translation["exchange"] = exchange
        translations[lang.name] = translation
    data["translations"] = translations
    return data

ENUM_COLS = ["name", "unit", "country", "category"]
def read_csv(path):
    df = pd.read_csv(path)
    df[ENUM_COLS] = df[ENUM_COLS].map(parse_enum)
    return df

ENUM_COLS_RAW = ["unit", "country", "language", "currency"]
def read_csv_raw(path):
    df = pd.read_csv(path)
    df[ENUM_COLS_RAW] = df[ENUM_COLS_RAW].map(parse_enum)
    df["categories"] = df["categories"].apply(lambda x: [parse_enum(c[:c.rfind(":")]) for c in re.sub(r'[\<\>\[\]]', "", x).split(", ")])
    return df