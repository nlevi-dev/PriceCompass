import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import io
import math
import gzip
import zipfile

import pandas as pd

from scrapers.types import *
from scrapers.exchange import CurrencyExchanger
from scrapers.items import ENUM_COLS

exchanger = CurrencyExchanger()

def generate_translations(lanuages=[Lang.EN]):
    # {
    #     "translations": {
    #         "EN": {
    #             "countries_raw": [],
    #             "categories_raw": [],
    #             "items_raw": [],
    #             "aggregate_raw": [],
    #             "countries_order": [],
    #             "categories_order": [],
    #             "items_order": [],
    #             "category_map": {},
    #         }
    #     }
    # }
    data = {}
    translations = {}
    for lang in lanuages:
        translation = {}
        translation["countries_raw"] = [enum_to_string(c, lang) for c in list(Country)[1:]]
        translation["categories_raw"] = [enum_to_string(c, lang) for c in list(Category)[1:]]
        translation["items_raw"] = [enum_to_string(c, lang) for c in list(Item)]
        translation["aggregate_raw"] = [enum_to_string(c, lang) for c in list(Aggregate)]
        translation["countries_order"] = sorted(translation["countries_raw"])
        translation["categories_order"] = translation["categories_raw"]
        translation["items_order"] = translation["items_order"]
        translations[lang.name] = translation
    data["translations"] = translations
    return data

def bits_to_int(bits, from_bit, length):
    shifted = bits >> from_bit
    mask = (1 << length) - 1
    return shifted & mask

def int_to_bits(number):
    return int(number)

def bits_to_float(bits, from_bit, len_mantissa, len_exponent):
    m_mask = (1 << len_mantissa) - 1
    m_bits = (bits >> from_bit) & m_mask
    e_mask = (1 << len_exponent) - 1
    e_bits = (bits >> (from_bit + len_mantissa)) & e_mask

    bias = (1 << (len_exponent - 1)) - 1
    max_e = e_mask

    if e_bits == max_e and m_bits == 0:
        return None

    if e_bits == 0:
        float_val = m_bits * (2 ** (1 - bias - len_mantissa))
    else:
        mantissa_value = 1 + (m_bits / (2 ** len_mantissa))
        actual_exponent = e_bits - bias
        float_val = mantissa_value * (2 ** actual_exponent)

    return float_val

def float_to_bits(number, len_mantissa, len_exponent):
    if number is None:
        max_e = (1 << len_exponent) - 1
        return max_e << len_mantissa

    if number == 0:
        return 0

    bias = (1 << (len_exponent - 1)) - 1
    max_e = (1 << len_exponent) - 1
    
    exponent = math.floor(math.log2(number))
    biased_exponent = exponent + bias

    if biased_exponent <= 0:
        e_bits = 0
        m_bits = round(number / (2 ** (1 - bias - len_mantissa)))
    elif biased_exponent >= max_e:
        e_bits = max_e - 1
        m_bits = (1 << len_mantissa) - 1
    else:
        e_bits = biased_exponent
        fractional_part = (number / (2 ** exponent)) - 1
        m_bits = round(fractional_part * (2 ** len_mantissa))

    return (e_bits << len_mantissa) | m_bits

#  1    1
#  2    3
#  3    7
#  4   15
#  5   31
#  6   63
#  7  127
#  8  255
#  9  511
# 10 1023
BITS_ITEM_LEN = 8      # bit length of a serialized item, limits the max unique items possible
BITS_COUNTRY_LEN = 5   # bit length of a serialized country, limits the max unique countries possible
BITS_PRICES_CNT = 10   # bit length of price count per item_country, limits the max entries for an item_country
BITS_PRICES_CNT_EXCEPTIONS = {
    Item.EATING_OUT: 13,
}
EXCHANGE_MANTISSA = 24
EXCHANGE_EXPONENT = 8
PRICE_MANTISSA = 13
PRICE_EXPONENT = 6
EXCHANGE_LEN = EXCHANGE_MANTISSA + EXCHANGE_EXPONENT
PRICE_LEN = PRICE_MANTISSA + PRICE_EXPONENT
BITS_COUNTRY_CNT = BITS_COUNTRY_LEN
MAX_ITEMS = (2 ** BITS_ITEM_LEN) - 1
MAX_COUNTRIES = (2 ** BITS_COUNTRY_LEN) - 1
MAX_COUNTRY_ITEM_COMBINATIONS = MAX_ITEMS * MAX_COUNTRIES
BITS_COUNTRY_ITEM_CNT = math.ceil(math.log2(MAX_COUNTRY_ITEM_COMBINATIONS + 1))

def serialize_df_num(df):
    # country_count
    # country exchange country exchange country exchange
    # country_count * item_count
    # item country
    # price_count
    # prices
    # item country
    # price_count
    # prices
    # item country
    # price_count
    # prices
    # rest_compressed
    bits = []

    bits.append([int_to_bits(len(lookup_currency)), BITS_COUNTRY_CNT])
    for country in lookup_currency.keys():
        bits.append([int_to_bits(country.value-1), BITS_COUNTRY_LEN])
        rate = exchanger.get_exchange_rate(lookup_currency[country], Currency.EUR)
        bits.append([float_to_bits(rate, EXCHANGE_MANTISSA, EXCHANGE_EXPONENT), EXCHANGE_LEN])
    
    unique_combinations = df[["name", "country"]].drop_duplicates()
    bits.append([int_to_bits(len(unique_combinations)), BITS_COUNTRY_ITEM_CNT])
    reordered_rows = []

    for _, row in unique_combinations.iterrows():
        item = row["name"]
        country = row["country"]
        
        item_country_data = df[(df["name"] == item) & (df["country"] == country)]
        price_count = len(item_country_data)
        
        variable_BITS_PRICES_CNT = BITS_PRICES_CNT
        if item in BITS_PRICES_CNT_EXCEPTIONS:
            variable_BITS_PRICES_CNT = BITS_PRICES_CNT_EXCEPTIONS[item]
        max_prices = (2 ** variable_BITS_PRICES_CNT) - 1
        if price_count > max_prices:
            print(f"Warning: Price count {price_count} for item {item} in country {country} exceeds maximum {max_prices}. Truncating to maximum.")
            price_count = max_prices
            item_country_data = item_country_data.head(max_prices)
        
        bits.append([int_to_bits(item.value-1), BITS_ITEM_LEN])
        bits.append([int_to_bits(country.value-1), BITS_COUNTRY_LEN])
        
        bits.append([int_to_bits(price_count), variable_BITS_PRICES_CNT])
        
        for _, price_row in item_country_data.iterrows():
            price = price_row["price"]
            bits.append([float_to_bits(price, PRICE_MANTISSA, PRICE_EXPONENT), PRICE_LEN])
            reordered_rows.append(price_row)
    
    total_bits = 0
    bit_position = 0
    for bit_value, bit_length in bits:
        total_bits |= (bit_value << bit_position)
        bit_position += bit_length
    total_bytes = (bit_position + 7) // 8
    df_reordered = pd.DataFrame(reordered_rows).reset_index(drop=True)
    return total_bits.to_bytes(total_bytes, byteorder="little"), df_reordered

def serialize_df_txt(df, compression="zip"):
    # vendor
    # link
    # original_name
    csv_data = df[["vendor", "link", "original_name"]].to_csv(index=False, header=False)
    
    if compression in ["zip"]:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("data.csv", csv_data)
        return zip_buffer.getvalue()
    elif compression in ["fflate", "gzip"]:
        return gzip.compress(csv_data.encode("utf-8"))
    else:
        return csv_data.encode("utf-8")

def serialize_df(df, compression="zip"):
    binary_data, df_reordered = serialize_df_num(df)
    txt_data = serialize_df_txt(df_reordered, compression)

    combined_data = binary_data + txt_data
    return combined_data

def deserialize_df_num(data):
    bits = int.from_bytes(data, byteorder="little")
    pos = 0

    country_count = bits_to_int(bits, pos, BITS_COUNTRY_CNT)
    pos += BITS_COUNTRY_CNT

    exchange_rates = {}
    for _ in range(country_count):
        country_idx = bits_to_int(bits, pos, BITS_COUNTRY_LEN)
        pos += BITS_COUNTRY_LEN
        rate = bits_to_float(bits, pos, EXCHANGE_MANTISSA, EXCHANGE_EXPONENT)
        pos += EXCHANGE_LEN
        exchange_rates[Country(country_idx + 1)] = rate

    combination_count = bits_to_int(bits, pos, BITS_COUNTRY_ITEM_CNT)
    pos += BITS_COUNTRY_ITEM_CNT

    rows = []
    for _ in range(combination_count):
        item_idx = bits_to_int(bits, pos, BITS_ITEM_LEN)
        pos += BITS_ITEM_LEN
        country_idx = bits_to_int(bits, pos, BITS_COUNTRY_LEN)
        pos += BITS_COUNTRY_LEN

        item = Item(item_idx + 1)
        country = Country(country_idx + 1)

        variable_BITS_PRICES_CNT = BITS_PRICES_CNT_EXCEPTIONS.get(item, BITS_PRICES_CNT)
        price_count = bits_to_int(bits, pos, variable_BITS_PRICES_CNT)
        pos += variable_BITS_PRICES_CNT

        for _ in range(price_count):
            price = bits_to_float(bits, pos, PRICE_MANTISSA, PRICE_EXPONENT)
            pos += PRICE_LEN
            rows.append({"name": item, "country": country, "price": price})

    num_bytes_used = (pos + 7) // 8
    return exchange_rates, rows, num_bytes_used

def deserialize_df_txt(data, compression="zip"):
    if compression in ["zip"]:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            csv_data = zf.read("data.csv").decode("utf-8")
    elif compression in ["fflate", "gzip"]:
        csv_data = gzip.decompress(data).decode("utf-8")
    else:
        csv_data = data.decode("utf-8")
    return pd.read_csv(io.StringIO(csv_data), header=None, names=["vendor", "link", "original_name"])

def deserialize_df(data, compression="zip"):
    exchange_rates, rows, num_bytes_used = deserialize_df_num(data)
    txt_df = deserialize_df_txt(data[num_bytes_used:], compression)

    df = pd.DataFrame(rows)
    df["vendor"] = txt_df["vendor"].values
    df["link"] = txt_df["link"].values
    df["original_name"] = txt_df["original_name"].values
    df["unit"] = df["name"].map(lambda item: lookup_filters[item][Unit.NONE])
    df["category"] = df["name"].map(lambda item: lookup_filters[item][Category.NONE])

    df = df[["name", "price", "unit", "country", "category", "vendor", "link", "original_name"]]

    return exchange_rates, df

def compare_by_rows(df1, df2, float_tolerance=[(1, 1e-4), (10, 1e-3), (100, 1e-2), (1000, 1e-1)]):
    if df1.shape != df2.shape:
        return False
    if not df1.columns.equals(df2.columns):
        return False
    
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    for col in ENUM_COLS:
        df1_copy[col] = df1_copy[col].astype(str)
        df2_copy[col] = df2_copy[col].astype(str)
    df1_sorted = df1_copy.sort_values(by=["original_name","category","name"]).reset_index(drop=True)
    df2_sorted = df2_copy.sort_values(by=["original_name","category","name"]).reset_index(drop=True)
    
    non_price_cols = [col for col in df1_sorted.columns if col != 'price']
    are_equal = df1_sorted[non_price_cols].equals(df2_sorted[non_price_cols])
    
    if are_equal and 'price' in df1_sorted.columns:
        price_diff = abs(df1_sorted['price'] - df2_sorted['price'])
        # Apply threshold-based tolerance
        tolerance_mask = pd.Series([True] * len(df1_sorted))
        for i in range(len(df1_sorted)):
            price_val = max(df1_sorted['price'].iloc[i], df2_sorted['price'].iloc[i])
            tolerance = 1  # default tolerance
            for threshold, tol in float_tolerance:
                if price_val <= threshold:
                    tolerance = tol
                    break
            tolerance_mask.iloc[i] = price_diff.iloc[i] <= tolerance
        are_equal = tolerance_mask.all()
    
    if not are_equal:
        # Print differing rows in pairs
        for i in range(len(df1_sorted)):
            row1 = df1_sorted.iloc[i]
            row2 = df2_sorted.iloc[i]
            rows_differ = False
            for col in df1_sorted.columns:
                if col == 'price':
                    price_val = max(row1[col], row2[col])
                    tolerance = 1  # default tolerance
                    for threshold, tol in float_tolerance:
                        if price_val <= threshold:
                            tolerance = tol
                            break
                    if abs(row1[col] - row2[col]) > tolerance:
                        rows_differ = True
                        break
                else:
                    if row1[col] != row2[col]:
                        rows_differ = True
                        break
            
            if rows_differ:
                print(f"Row {i} differs:")
                print(f"  df1: {row1.to_dict()}")
                print(f"  df2: {row2.to_dict()}")
    
    return are_equal
