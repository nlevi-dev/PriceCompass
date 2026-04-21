import { bitsToBaseN, baseNtoBits, bitsToInt, intToBits, bitsToFloat, floatToBits, bitsToBitmask, bitmaskToBits, appendBits } from './utils';
import { compressBigIntSync, decompressBigIntSync } from './compress';
import settings from '../settings.json';
import * as fflate from 'fflate';

const S = settings.settings;

// used for deserializing the binary data
const BITS_ITEM_LEN              = S.BITS_ITEM_LEN;
const BITS_COUNTRY_LEN           = S.BITS_COUNTRY_LEN;
const BITS_PRICES_CNT            = S.BITS_PRICES_CNT;
const BITS_PRICES_CNT_EXCEPTIONS = S.BITS_PRICES_CNT_EXCEPTIONS;
const EXCHANGE_MANTISSA          = S.EXCHANGE_MANTISSA;
const EXCHANGE_EXPONENT          = S.EXCHANGE_EXPONENT;
const PRICE_MANTISSA             = S.PRICE_MANTISSA;
const PRICE_EXPONENT             = S.PRICE_EXPONENT;

// used for url encoding
const BITS_AGG_LEN      = S.BITS_AGG_LEN;
const BITS_CATEGORY_LEN = S.BITS_CATEGORY_LEN;
//BITS_ITEMS_LEN
const BITS_COUNTRY_CNT  = S.BITS_COUNTRY_CNT;
//BITS_COUNTRY_LEN
const BITS_COUNT_LEN    = S.BITS_COUNT_LEN;
const DECIMAL2EDGE      = S.DECIMAL2EDGE;
const DECIMAL1EDGE      = S.DECIMAL1EDGE;

// helpers
const EXCHANGE_LEN = EXCHANGE_MANTISSA + EXCHANGE_EXPONENT
const PRICE_LEN = PRICE_MANTISSA + PRICE_EXPONENT
const MAX_ITEMS = Math.pow(2, BITS_ITEM_LEN) - 1
const MAX_COUNTRIES = Math.pow(2, BITS_COUNTRY_LEN) - 1
const MAX_COUNTRY_ITEM_COMBINATIONS = MAX_ITEMS * MAX_COUNTRIES
const BITS_COUNTRY_ITEM_CNT = Math.ceil(Math.log2(MAX_COUNTRY_ITEM_COMBINATIONS + 1))
const AUX1 = DECIMAL2EDGE * 100;
const AUX2 = AUX1 + (DECIMAL1EDGE - DECIMAL2EDGE) * 10;

function intToCustomFixed(num) {
    if (num <= AUX1)
        return num / 100;
    if (num <= AUX2)
        return DECIMAL2EDGE + (num - AUX1) / 10;
    return DECIMAL1EDGE + (num - AUX2);
}

function customFixedToInt(num) {
    if (num <= DECIMAL2EDGE)
        return Math.round(num * 100);
    if (num <= DECIMAL1EDGE)
        return AUX1 + Math.round((num - DECIMAL2EDGE) * 10);
    return AUX2 + Math.round(num - DECIMAL1EDGE);
}

export function stateManage(state, countriesMap, categoriesMap, aggregateMap, itemsMap) {
    let aggMethod;
    let collapsedCategories;
    let unLinkedItems;
    let selectedCountries;
    let itemCounts;
    let selectedItem;
    try {
        let bits = baseNtoBits(state);

        let idx = 0;
        let len = 0;

        len = 1;
        const isCompressed = Boolean(bitsToInt(bits, idx, len));
        if (isCompressed) {
            bits = decompressBigIntSync(bits >> 1n);
        } else {
            idx += len;
        }

        len = BITS_AGG_LEN;
        aggMethod = aggregateMap[bitsToInt(bits, idx, len)];
        idx += len;

        len = BITS_CATEGORY_LEN;
        const categoryCount = bitsToInt(bits, idx, len);
        idx += len;

        len = categoryCount;
        const collapsedCategoriesBitmask = bitsToBitmask(bits, idx, len);
        collapsedCategories = [];
        for (let i = 0; i < collapsedCategoriesBitmask.length; i++)
            if (collapsedCategoriesBitmask[i])
                collapsedCategories.push(categoriesMap[i]);
        idx += len;

        len = BITS_ITEMS_LEN;
        const itemCount = bitsToInt(bits, idx, len);
        idx += len;

        len = itemCount;
        const unLinkedItemsBitmask = bitsToBitmask(bits, idx, len);
        unLinkedItems = [];
        for (let i = 0; i < unLinkedItemsBitmask.length; i++)
            if (unLinkedItemsBitmask[i])
                unLinkedItems.push(itemsMap[i]);
        idx += len;

        len = BITS_COUNTRY_CNT;
        const countryCount = bitsToInt(bits, idx, len);
        idx += len;

        selectedCountries = [];
        itemCounts = {};
        let primaryCountry;
        for (let i = 0; i < countryCount; i++) {
            len = BITS_COUNTRY_LEN;
            const country = countriesMap[bitsToInt(bits, idx, len)];
            idx += len;
            selectedCountries.push(country);
            if (i === 0)
                primaryCountry = country;
            for (let j = 0; j < itemsMap.length; j++) {
                len = BITS_COUNT_LEN;
                const cnt = intToCustomFixed(bitsToInt(bits, idx, len));
                idx += len;
                if (i === 0)
                    itemCounts[itemsMap[j]] = {};
                if (i === 0 || unLinkedItems.includes(itemsMap[j]))
                    itemCounts[itemsMap[j]][country] = cnt;
                else
                    itemCounts[itemsMap[j]][country] = itemCounts[itemsMap[j]][primaryCountry];
            }
        }

        len = BITS_ITEMS_LEN;
        selectedItem = itemsMap[bitsToInt(bits, idx, len)];
        idx += len;

        len = 1;
        const isSelectedItem = Boolean(bitsToInt(bits, idx, len));
        idx += len;

        if (!isSelectedItem) {
            selectedItem = null;
        }
    } catch (error) {
        console.error(error);
        aggMethod = aggregateMap[0];
        collapsedCategories = [];
        unLinkedItems = [];
        selectedCountries = [];
        itemCounts = {};
        selectedItem = null;
    }

    const serializeState = (aggMethod, collapsedCategories, unLinkedItems, selectedCountries, itemCounts, selectedItem, countryChanged = null) => {
        if (countryChanged === null)
            countryChanged = selectedCountries[0];

        let bits = [];

        let aggregateIdx = aggregateMap.findIndex(a => a === aggMethod);
        if (aggregateIdx < 0) {
            aggregateIdx = 0;
            console.error("Aggregate mode not found!");
        }
        bits.push([intToBits(aggregateIdx), BITS_AGG_LEN]);

        const categoryCount = categoriesMap.length;
        bits.push([intToBits(categoryCount), BITS_CATEGORY_LEN]);

        const collapsedCategoriesBitmask = categoriesMap.map(c => collapsedCategories.includes(c));
        bits.push([bitmaskToBits(collapsedCategoriesBitmask), categoriesMap.length]);

        const itemCount = itemsMap.length;
        bits.push([intToBits(itemCount), BITS_ITEMS_LEN]);

        const unLinkedItemsBitmask = itemsMap.map(c => unLinkedItems.includes(c));
        bits.push([bitmaskToBits(unLinkedItemsBitmask), itemsMap.length]);

        const countryCount = selectedCountries.length;
        bits.push([intToBits(countryCount), BITS_COUNTRY_CNT]);

        let allCnt = 0;
        for (let i = 0; i < countryCount; i++) {
            let countryIdx = countriesMap.findIndex(c => c === selectedCountries[i]);
            if (countryIdx < 0) {
                countryIdx = 0;
                console.error("Country not found!")
            }
            bits.push([intToBits(countryIdx), BITS_COUNTRY_LEN]);
            for (let j = 0; j < itemCount; j++) {
                if (unLinkedItems.includes(itemsMap[j])) {
                    const val = itemCounts[itemsMap[j]]?.[countriesMap[countryIdx]] ?? 0;
                    allCnt += val;
                    bits.push([intToBits(customFixedToInt(val)), BITS_COUNT_LEN]);
                } else {
                    const countryIdx2 = countriesMap.findIndex(c => c === countryChanged);
                    const val2 = itemCounts[itemsMap[j]]?.[countriesMap[countryIdx2]] ?? 0;
                    allCnt += val2;
                    bits.push([intToBits(customFixedToInt(val2)), BITS_COUNT_LEN]);
                }
                    
            }
        }

        if (selectedItem) {
            const itemIdx = itemsMap.findIndex(c => c === selectedItem);
            bits.push([intToBits(itemIdx), BITS_ITEMS_LEN]);
            bits.push([intToBits(1), 1]);
        } else {
            bits.push([intToBits(0), BITS_ITEMS_LEN]);
            bits.push([intToBits(0), 1]);
        }
        
        const uncompressed = appendBits(bits);
        const compressed = compressBigIntSync(uncompressed);
        const uncompressedLen = uncompressed.toString(2).length;
        const compressedLen = compressed.toString(2).length;
        const diff = uncompressedLen - compressedLen;
        if (diff < 0)
            return bitsToBaseN(appendBits([[0,1],[uncompressed,uncompressedLen]]));
        else
            return bitsToBaseN(appendBits([[1,1],[compressed,compressedLen]]));
    };

    return [
        aggMethod,
        collapsedCategories,
        unLinkedItems,
        selectedCountries,
        itemCounts,
        selectedItem,
        serializeState,
    ];
}

export function deserializeBin(arrayBuffer, lang="EN") {
    const translation    = settings.translations[lang];
    const items_raw      = translation.items_raw;      // index -> item name
    const countries_raw  = translation.countries_raw;  // index -> country name
    const categories_raw = translation.categories_raw; // index -> category name
    const units_raw      = translation.units_raw;      // index -> unit name
    const category_map   = settings.category_map;      // item index -> category index
    const unit_map       = settings.unit_map;          // item index -> unit index

    const bytes = new Uint8Array(arrayBuffer);

    let bits = 0n;
    for (let i = bytes.length - 1; i >= 0; i--)
        bits = (bits << 8n) | BigInt(bytes[i]);

    let pos = 0;

    const countryCount = bitsToInt(bits, pos, BITS_COUNTRY_CNT);
    pos += BITS_COUNTRY_CNT;

    const exchange = {};
    for (let i = 0; i < countryCount; i++) {
        const countryIdx = bitsToInt(bits, pos, BITS_COUNTRY_LEN);
        pos += BITS_COUNTRY_LEN;
        const rate = bitsToFloat(bits, pos, EXCHANGE_MANTISSA, EXCHANGE_EXPONENT);
        pos += EXCHANGE_LEN;
        exchange[countries_raw[countryIdx]] = rate;
    }

    const combinationCount = bitsToInt(bits, pos, BITS_COUNTRY_ITEM_CNT);
    pos += BITS_COUNTRY_ITEM_CNT;

    const rows = [];
    for (let i = 0; i < combinationCount; i++) {
        const itemIdx    = bitsToInt(bits, pos, BITS_ITEM_LEN);    pos += BITS_ITEM_LEN;
        const countryIdx = bitsToInt(bits, pos, BITS_COUNTRY_LEN); pos += BITS_COUNTRY_LEN;

        const variableCnt = BITS_PRICES_CNT_EXCEPTIONS[String(itemIdx)] ?? BITS_PRICES_CNT;
        const priceCount  = bitsToInt(bits, pos, variableCnt);
        pos += variableCnt;

        for (let j = 0; j < priceCount; j++) {
            const price = bitsToFloat(bits, pos, PRICE_MANTISSA, PRICE_EXPONENT);
            pos += PRICE_LEN;
            rows.push({ itemIdx, countryIdx, price });
        }
    }

    const numBytesUsed = Math.ceil(pos / 8);

    const gzipBytes = bytes.slice(numBytesUsed);
    const csvBytes  = fflate.gunzipSync(gzipBytes);
    const csvText   = new TextDecoder().decode(csvBytes);

    const csvLines = csvText.split("\n");
    if (csvLines[csvLines.length - 1] === "") csvLines.pop();

    const data = {};
    for (let i = 0; i < rows.length; i++) {
        const { itemIdx, countryIdx, price } = rows[i];
        const parts = csvLines[i].split(",");
        const vendor        = parts[0];
        const link          = parts[1];
        const original_name = parts.slice(2, parts.length).join(",");
        const itemName     = items_raw[itemIdx];
        const countryName  = countries_raw[countryIdx];
        const categoryName = categories_raw[category_map[itemIdx]];
        const unitName     = units_raw[unit_map[itemIdx]];

        if (!data[categoryName])
            data[categoryName] = {};
        if (!data[categoryName][countryName])
            data[categoryName][countryName] = {};
        if (!data[categoryName][countryName][itemName])
            data[categoryName][countryName][itemName] = { unit: unitName, items: [] };

        data[categoryName][countryName][itemName].items.push({ price, vendor, link, name: original_name });
    }

    return [ exchange, data ];
}
