import { bitsToBaseN, baseNtoBits, bitsToInt, intToBits, bitsToFloat, floatToBits, bitsToBitmask, bitmaskToBits, appendBits } from './baseN';
import { compressBigIntSync, decompressBigIntSync } from './compress';

//  1    1
//  2    3
//  3    7
//  4   15
//  5   31
//  6   63
//  7  127
//  8  255
//  9  511
// 10 1023

const BITS_AGG_LEN = 4;
const BITS_CATEGORY_LEN = 5; 
//const BITS_CATEGORY_MASK = Math.pow(2, BITS_CATEGORY_CNT) - 1; //(max value)
const BITS_ITEMS_LEN = 8;
//const BITS_ITEMS_MASK = Math.pow(2, BITS_ITEMS_CNT) - 1; //(max value)
const BITS_COUNTRY_CNT = 3;
const BITS_COUNTRY_LEN = 5;
const BITS_COUNT_LEN = 9;
//const BITS_ITEMS_COUNTS = (Math.pow(2, BITS_ITEMS_CNT) - 1) * BITS_COUNT_LEN; //(max value)
// with max 3 countries and base 62, results in max 1339 chars
// 4 1768

const DECIMAL2EDGE = 2;
const DECIMAL1EDGE = 20;
const AUX1 = DECIMAL2EDGE*100;
const AUX2 = AUX1+(DECIMAL1EDGE-DECIMAL2EDGE)*10;
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
    let selectedCategory;
    let openedItems;
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

        len = BITS_CATEGORY_LEN;
        selectedCategory = categoriesMap[bitsToInt(bits, idx, len)];
        idx += len;

        len = 1;
        const isSelectedCategory = Boolean(bitsToInt(bits, idx, len));
        idx += len;

        if (!isSelectedCategory) {
            selectedCategory = null;
        }

        len = itemCount;
        const openedItemsBitmask = bitsToBitmask(bits, idx, len);
        openedItems = [];
        for (let i = 0; i < openedItemsBitmask.length; i++)
            if (openedItemsBitmask[i])
                openedItems.push(itemsMap[i]);
        idx += len;
    } catch (error) {
        console.error(error);
        aggMethod = aggregateMap[0];
        collapsedCategories = [];
        unLinkedItems = [];
        selectedCountries = [];
        itemCounts = {};
        selectedCategory = null;
        openedItems = [];
    }

    const serializeState = (aggMethod, collapsedCategories, unLinkedItems, selectedCountries, itemCounts, selectedCategory, openedItems, countryChanged = null) => {
        if (countryChanged === null)
            countryChanged = selectedCountries[0];

        let bits = [];

        const aggregateIdx = aggregateMap.findIndex(a => a === aggMethod);
        if (aggregateIdx < 0)
            throw new Error("Aggregate mode not found!");
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
            const countryIdx = countriesMap.findIndex(c => c === selectedCountries[i]);
            if (countryIdx < 0)
                throw new Error("Country not found!");
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

        if (selectedCategory && allCnt > 0) {
            const categoryIdx = categoriesMap.findIndex(c => c === selectedCategory);
            bits.push([intToBits(categoryIdx), BITS_CATEGORY_LEN]);
            bits.push([intToBits(1), 1]);
        } else {
            bits.push([intToBits(0), BITS_CATEGORY_LEN]);
            bits.push([intToBits(0), 1]);
        }

        if (allCnt > 0) {
            const openedItemsBitmask = itemsMap.map(c => openedItems.includes(c));
            bits.push([bitmaskToBits(openedItemsBitmask), itemsMap.length]);
        } else {
            bits.push([intToBits(0), itemsMap.length]);
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
        selectedCategory,
        openedItems,
        serializeState,
    ];
}