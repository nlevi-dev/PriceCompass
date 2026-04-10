// {
//     "date": "2026-03-24",
//     "translations": {
//         "EN": {
//             "data": [
//                 {
//                     "category": "Meat and Fish",
//                     "countries": {
//                         "Hungary": [
//                             {
//                                 "name": "Pork Mince",
//                                 "unit": "kg",
//                                 "items": [
//                                     {
//                                         "price": 1,
//                                         "vendor": "auchan.hu",
//                                         "link": "[LINK]",
//                                         "name": "daralt hus",
//                                     }
//                                 ]
//                             }
//                         ]
//                     },
//                 }
//             ],
//             "countries": ["Hungary"],
//             "countries_raw": [],
//             "categories_raw": [],
//             "aggregate_raw": [],
//             "items_raw": [],
//             "exchange": {"Hungary":{"currency":"HUF","value":1}},
//         }
//     }
// }

export function parseData(jsonData, lang = 'EN') {
    const date = jsonData.date;
    const tmp = jsonData.translations[lang];
    const data = tmp.data;
    const countries = tmp.countries;
    const exchange = tmp.exchange;
    const itemsPerCategory = {};
    const itemsAll = [];
    const countriesMap = tmp.countries_raw;
    const categoriesMap = tmp.categories_raw;
    const aggregateMap = tmp.aggregate_raw;
    const itemsMap = tmp.items_raw;

    data.forEach(categoryObj => {
        const categoryName = categoryObj.category;
        if (!itemsPerCategory[categoryName]) {
            itemsPerCategory[categoryName] = [];
        }
        Object.values(categoryObj.countries).forEach(productsInCountry => {
            productsInCountry.forEach(product => {
                if (!itemsPerCategory[categoryName].map(p => p.name).includes(product.name)) {
                    itemsPerCategory[categoryName].push(product);
                }
                if (!itemsAll.map(p => p.name).includes(product.name)) {
                    itemsAll.push(product);
                }
            });
        });
    });

    return [
        Object.keys(jsonData.translations),
        date,
        countries,
        exchange,
        itemsPerCategory,
        itemsAll,
        data,
        countriesMap,
        categoriesMap,
        aggregateMap,
        itemsMap,
    ];
}

export function filterData(data, exchange, countries) {
    const dataFiltered = data.map(categoryObj => {
        const filteredCountries = {};
        Object.keys(categoryObj.countries).forEach(countryName => {
            if (countries.includes(countryName)) {
                filteredCountries[countryName] = categoryObj.countries[countryName];
            }
        });
        return {
            ...categoryObj,
            countries: filteredCountries
        };
    }).filter(categoryObj => {
        return Object.keys(categoryObj.countries).length > 0;
    });

    const exchangeFiltered = {};
    countries.forEach(country => {
        if (exchange[country]) {
            exchangeFiltered[country] = exchange[country];
        }
    });

    return [
        dataFiltered,
        exchangeFiltered,
    ];
}

export function aggregateData(data, method = 0) {
    if (data.length == 0) {
        return data;
    }
    return data.map(categoryObj => {
        const updatedCountries = {};
        for (const [country, products] of Object.entries(categoryObj.countries)) {
            updatedCountries[country] = products.map(product => {
                const prices = product.items.map(item => item.price);
                
                let aggregatePrice = 0;
                if (prices.length > 0) {
                    if (method === 0) {
                        const sum = prices.reduce((a, b) => a + b, 0);
                        aggregatePrice = sum / prices.length;
                    } else if (method === 1) {
                        aggregatePrice = Math.min(...prices);
                    } else {
                        aggregatePrice = Math.max(...prices);
                    }
                }
                return {
                    name: product.name,
                    unit: product.unit,
                    price: aggregatePrice,
                    items: product.items
                };
            });
        }
        return {
            ...categoryObj,
            countries: updatedCountries
        };
    });
}

export function toCsv(data) {
    const headers = ["name", "category", "price", "unit", "country", "vendor", "link", "original_name"];
    const rows = [];

    rows.push(headers.join(","));

    data.forEach(categoryObj => {
        const category = categoryObj.category;

        Object.entries(categoryObj.countries).forEach(([country, products]) => {
            products.forEach(product => {
                const { name, unit, items } = product;

                items.forEach(item => {
                    const row = [
                        `"${name}"`,        // Parent product name
                        `"${category}"`,    // Category
                        item.price,         // Individual item price
                        `"${unit}"`,        // Unit (kg, etc)
                        `"${country}"`,     // Country name
                        `"${item.vendor}"`, // Vendor (auchan.hu, etc)
                        `"${item.link}"`,   // URL
                        `"${item.name}"`    // Original name (daralt hus)
                    ];
                    rows.push(row.join(","));
                });
            });
        });
    });

    return rows.join("\n");
}

export function toPieData(data, itemCounts, countriesMap, categoriesMap) {
    const piesPerCountry = countriesMap.reduce((acc, country) => {acc[country] = categoriesMap.map((category, idx) => {return {"name": category, "idx": idx, "sum": 0};}); return acc;}, {});
    const pieCategoriesActive = categoriesMap.map((category, idx) => {return {"name": category, "idx": idx, "sum": 0};});
    let allSum = 0;
    const sumsPerCountry = countriesMap.reduce((acc, country) => {acc[country] = 0; return acc;}, {});

    data.forEach((categoryObj, catIdx) => {
        for (const [country, products] of Object.entries(categoryObj.countries)) {
            products.forEach(product => {
                const price = product.price * (itemCounts[product.name]?.[country] ?? 0) / 10;
                piesPerCountry[country][catIdx].sum += price;
                sumsPerCountry[country] += price;
                allSum += price;
                pieCategoriesActive[catIdx].sum += price;
            });
        }
    });

    const maxResult = Math.ceil(Math.max(...Object.values(piesPerCountry).flatMap(cats => cats.map(c => c.sum))) / 5) * 5;

    return [ allSum, piesPerCountry, sumsPerCountry, maxResult, pieCategoriesActive.filter(c => c.sum > 0) ];
}

export function toItemData(data, itemCounts, countriesMap, itemsMap, selectedCategory) {
    const linksPerCountry = countriesMap.reduce((acc, country) => {acc[country] = {}; return acc;}, {});
    const itemsActive = [];

    data.forEach(categoryObj => {
        if (categoryObj.category === selectedCategory)
            for (const [country, products] of Object.entries(categoryObj.countries)) {
                products.forEach(product => {
                    const count = (itemCounts[product.name]?.[country] ?? 0);
                    if (count > 0 && !itemsActive.includes(product.name))
                        itemsActive.push(product.name);
                    linksPerCountry[country][product.name] = product;
                });
            }
    });

    const maxLinkCountPerItem = {};

    itemsActive.forEach(item => {
        countriesMap.forEach(country => {
            const cnt = linksPerCountry[country][item].items.length;
            maxLinkCountPerItem[item] = Math.max(maxLinkCountPerItem[item] ?? 0, cnt);
        });
    });

    return [ linksPerCountry, itemsMap.filter(a => itemsActive.includes(a)), maxLinkCountPerItem ];
}