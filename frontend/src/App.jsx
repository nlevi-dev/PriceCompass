import React, { useMemo, useState } from 'react';
import CollapseButton from './components/CollapseButton';
import LinkButton from './components/LinkButton';
import PieChart, { generateColors } from './components/PieChart';
import BarChart from './components/BarChart';
import { useLocalStorage } from './hooks/useLocalStorage';
import { useQueryState } from './hooks/useQueryState';
import { parseData, filterData, aggregateData, toCsv, toPieData, toItemData } from './utils/dataParser';
import { stateManage } from './utils/querySerializer';
import rawData from './data.json';

function App() {
    const [language, setLanguage] = useLocalStorage('lang', 'EN');
    const [state, setState] = useQueryState('s', '', false);

    const [
        languages,
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
    ] = useMemo(() => parseData(rawData, language), [language]);

    const [
        aggMethod,
        collapsedCategories,
        unLinkedItems,
        selectedCountries,
        itemCounts,
        selectedCategory,
        openedItems,
        serializeState,
    ] = stateManage(state, countriesMap, categoriesMap, aggregateMap, itemsMap);

    const [ dataFiltered, exchangeFiltered ] = useMemo(() => filterData(data, exchange, selectedCountries), [language, selectedCountries]);
    const dataAgg = useMemo(() => aggregateData(dataFiltered, aggregateMap.findIndex(a => a === aggMethod)), [language, selectedCountries, aggMethod]);

    const exportCSV = () => {
        const csvString = toCsv(data);
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `${date}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const handleReset = () => {
        setState(serializeState(aggMethod, [], [], selectedCountries, {}, selectedCategory));
    };

    const formatCurrency = (currency) => {
        return currency.toFixed(2);
    }

    const [ pieSum, pieData, sumsPerCountry, maxPerCountry, pieCategoriesActive ] = toPieData(dataAgg, itemCounts, selectedCountries, categoriesMap);

    const pieColors = useMemo(() => generateColors(categoriesMap.length), [categoriesMap.length]);
    const [pieHighlightedCategory, setPieHighlightedCategory] = useState(null);
    const [rowHighlightedCategory, setRowHighlightedCategory] = useState(null);
    
    const [ linksPerCountry, itemsActive, maxLinkCountPerItem ] = toItemData(dataAgg, itemCounts, selectedCountries, itemsMap, selectedCategory);

    const setSelectedCountries = (a) => setState(serializeState(aggMethod, collapsedCategories, unLinkedItems, a, itemCounts, null, []));
    const setCollapsedCategories = (a) => setState(serializeState(aggMethod, a, unLinkedItems, selectedCountries, itemCounts, selectedCategory, openedItems));
    const setAggMethod = (a) => setState(serializeState(a, collapsedCategories, unLinkedItems, selectedCountries, itemCounts, selectedCategory, openedItems));
    const setUnLinkedItems = (a) => setState(serializeState(aggMethod, collapsedCategories, a, selectedCountries, itemCounts, selectedCategory, openedItems));
    const setItemCounts = (a, countryChanged) => setState(serializeState(aggMethod, collapsedCategories, unLinkedItems, selectedCountries, a, selectedCategory, openedItems.filter(item => itemsActive.includes(item)), countryChanged));
    const setSelectedCategory = (a) => setState(serializeState(aggMethod, collapsedCategories, unLinkedItems, selectedCountries, itemCounts, a, []));
    const setOpenedItems = (a) => setState(serializeState(aggMethod, collapsedCategories, unLinkedItems, selectedCountries, itemCounts, selectedCategory, a));

    return (
        <div className="flex flex-col min-h-screen">
            {/* Header */}
            <header className="flex justify-between sticky top-0 p-4 bg-gray-500 z-10">
                <div className="flex items-center space-x-5">
                    <h1>Price Compass - International Price of Living Comparator</h1>
                </div>
                <div className="flex items-center space-x-5">
                    <div className="flex items-center">
                        <p>Language:&nbsp;</p>
                        <select value={language} onChange={e => setLanguage(e.target.value)}>
                            {languages.map(lang => <option key={lang} value={lang}>{lang}</option>)}
                        </select>
                    </div>
                </div>
            </header>

            {/* Welcome Section */}
            <section className="p-4">
                <div className="max-w-7xl mx-auto w-full" style={{textAlign:"justify"}}>
                    <p>
                        Price Compass is an open-source tool designed to provide a granular, verifiable look at the cost of living across borders. 
                        Unlike traditional cost-of-living indexes that offer "black box" metrics, we serve both aggregated insights and the 
                        underlying raw data, allowing you to verify, audit, and calculate your own economic indicators.
                    </p>
                    <br/>
                    <h3>Key Features:</h3>
                    <ul>
                        <li style={{listStyleType:"disc",marginLeft:"30px"}}><strong>Custom "Shopping Baskets":</strong> Define your own lifestyle. Instead of generic averages, build a monthly cart reflecting what <em>you</em> actually consume.</li>
                        <li style={{listStyleType:"disc",marginLeft:"30px"}}><strong>Radical Transparency:</strong> Access the raw, non-aggregated data points. Every price is tagged with a vendor name and a link to the product.</li>
                        <li style={{listStyleType:"disc",marginLeft:"30px"}}><strong>On-the-Fly Aggregation:</strong> Switch between aggregation modes such as <strong>Average</strong>, <strong>Minimum</strong>, or <strong>Maximum</strong> to instantly see the full market spectrum.</li>
                    </ul>
                    <br/>
                    <p>
                        For more legal, ethical, and technical details, please visit the GitHub page located in the contacts section at the bottom.
                    </p>
                </div>
            </section>

            {/* Settings Section */}
            <section className="p-4 bg-gray-200 border-y">
                <div className="flex justify-between">
                    <div className="flex items-center space-x-5">
                        <select
                            value=""
                            disabled={selectedCountries.length >= 3}
                            style={selectedCountries.length >= 3?{opacity: 0.5, cursor: 'not-allowed'}:{}}
                            onChange={e => {
                                const val = e.target.value;
                                if (val) {
                                    if (!selectedCountries.includes(val)) {
                                        setSelectedCountries([...selectedCountries, val]);
                                    }
                                }
                            }}
                        >
                            <option value="" disabled hidden>Add Country...</option>
                            {countries.filter(c => !selectedCountries.includes(c)).map(c => (
                                <option key={c} value={c}>
                                    {c}
                                </option>
                            ))}
                        </select>

                        <div className="flex gap-2">
                            {selectedCountries.map(c => (
                                <span key={c} className="bg-blue-200 px-2 py-1 rounded">
                                    {c} <button onClick={() => {setSelectedCountries(selectedCountries.filter(co => co !== c));}}>x</button>
                                </span>
                            ))}
                        </div>
                        
                        <div className="flex items-center">
                            <p>Aggregation Mode:&nbsp;</p>
                            <select value={aggMethod} onChange={e => setAggMethod(e.target.value)}>
                                {aggregateMap.map(a => (<option key={a} value={a}>{a}</option>))}
                            </select>
                        </div>
                    </div>
                    <div className="flex items-center space-x-5">
                        <button onClick={exportCSV} className="bg-gray-500 text-white px-3 py-1">Export CSV</button>

                        <button onClick={handleReset} className="bg-red-500 text-white px-3 py-1">Reset</button>
                    </div>
                </div>
            </section>

            {/* Aux Info Section */}
            <section className="p-4">
                <div className="max-w-7xl mx-auto w-full">
                    <p>Scraped at: {date}</p>
                    <br/>

                    {Object.keys(exchangeFiltered).length > 0 && (<p>Currency exchange:</p>)}
                    {Object.keys(exchangeFiltered).length > 0 && (<table className="table_currency"><tbody>
                        <tr>
                            <td className="text-left"></td>
                            <td className="text-right">EUR</td>
                        </tr>
                        {Object.keys(exchangeFiltered).map((key) => (<tr key={key}>
                            <td className="text-left">{exchange[key].currency}</td>
                            <td className="text-right font-mono">{formatCurrency(exchange[key].value)}</td>
                        </tr>))}
                    </tbody></table>)}
                </div>
            </section>

            {/* Main Compare Section */}
            {selectedCountries.length === 0 && (<h1 className="mt-20 flex-grow w-full text-center text-2xl font-semibold">Add a country to start browsing items!</h1>)}
            {selectedCountries.length > 0 && (<section className="p-4 flex-grow">
                <div className="max-w-7xl mx-auto w-full">
                    <div className="overflow-auto max-h-[80vh] pb-4">
                        <table className="table_compare_1 min-w-full"><tbody>
                            <tr className="table_compare_1_header_1">
                                <td rowSpan="2" className="w-[1%]"><LinkButton size={30} isLinked={unLinkedItems.length == 0}  onToggle={(isLinked) => {
                                    if (isLinked)
                                        setUnLinkedItems([]);
                                    else
                                        setUnLinkedItems(itemsAll.map(p => p.name));
                                }}/></td>
                                <td rowSpan="2">name</td>
                                <td rowSpan="2" style={{"width":"6em"}}>unit<br/><div style={{"fontWeight":"normal","fontStyle":"italic"}}>(EUR/)</div></td>
                                {selectedCountries.map(country => (
                                    <td key={country} colSpan="3">{country}</td>
                                ))}
                            </tr>
                            <tr className="table_compare_1_header_2">{selectedCountries.map(country => (<React.Fragment key={country}>
                                <td style={{"width":"6em"}}>count</td>
                                <td style={{"width":"6em"}}>price</td>
                                <td style={{"width":"6em"}}>sum</td></React.Fragment>))}
                            </tr>
                            {dataAgg.map(cat => (<React.Fragment key={cat.category}>
                                <tr>
                                    <td><LinkButton size={18} isLinked={!itemsPerCategory[cat.category].some(item => unLinkedItems.includes(item.name))} onToggle={(isLinked) => {
                                        if (isLinked)
                                            setUnLinkedItems(unLinkedItems.filter(n => !itemsPerCategory[cat.category].map(p => p.name).includes(n)));
                                        else
                                            setUnLinkedItems([...new Set([...unLinkedItems, ...itemsPerCategory[cat.category].map(p => p.name)])]);
                                    }}/></td>
                                    <td className="table_compare_1_category" colSpan={(2+selectedCountries.length*3)}>
                                        <CollapseButton isOpen={!collapsedCategories.includes(cat.category)} onToggle={(isOpen) => {
                                            if (isOpen)
                                                setCollapsedCategories(collapsedCategories.filter(cc => cc !== cat.category));
                                            else
                                                setCollapsedCategories([...collapsedCategories, cat.category]);
                                        }}/>
                                        &nbsp;{cat.category}
                                    </td>
                                </tr>
                                {!collapsedCategories.includes(cat.category) && 
                                    itemsPerCategory[cat.category].map(item => (<tr key={item.name}>
                                        <td><LinkButton isLinked={!unLinkedItems.includes(item.name)} onToggle={(isLinked) => {
                                            if (isLinked)
                                                setUnLinkedItems(unLinkedItems.filter(n => n !== item.name));
                                            else
                                                setUnLinkedItems([...unLinkedItems, item.name]);
                                        }}/></td>
                                        <td style={{"textAlign":"left"}}>{item.name}</td>
                                        <td dangerouslySetInnerHTML={{ __html: item.unit }}/>
                                        {selectedCountries.map(country => (<React.Fragment key={country}>
                                            <td><input type="number" step="1" min="0" max="100"
                                                className="w-16 text-center w-16 text-center border border-gray-300 rounded px-2 py-1 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                value={itemCounts[item.name]?.[country] ?? 0}
                                                onChange={(ev) => {
                                                    const val = Math.min(parseFloat(ev.target.value) || 0, 100);
                                                    setItemCounts({
                                                        ...itemCounts,
                                                        [item.name]: {
                                                            ...itemCounts[item.name],
                                                            [country]: val
                                                        }
                                                    }, country);
                                                }}
                                            /></td>                                   
                                            <td style={{"textAlign":"right"}} className="font-mono">{formatCurrency(cat.countries[country].find(item2 => item2.name == item.name).price)}</td>
                                            <td style={{"textAlign":"right"}} className="font-mono">{formatCurrency(cat.countries[country].find(item2 => item2.name == item.name).price * itemCounts[item.name][country])}</td>
                                        </React.Fragment>))}
                                    </tr>))
                                }
                            </React.Fragment>))}
                        </tbody></table>
                    </div>
                </div>
            </section>)}

            {/* Category Breakdown Section */}
            {(selectedCountries.length > 0 && pieSum === 0) && (<h1 className="mt-20 w-full text-center text-2xl font-semibold mb-20">Add items to your selection!</h1>)}
            {(selectedCountries.length > 0 && pieSum > 0) && (<section className="p-4">
                <div className="max-w-7xl mx-auto w-full">
                    <div className="overflow-auto pb-4">
                        <table className="table_compare_1 min-w-full"><tbody>
                            <tr className="table_compare_1_header_1"><td className="w-px"></td>{selectedCountries.map(country => (<td key={country}>{country}</td>))}</tr>
                            <tr>
                                <td style={{textAlign:"left"}}>sum <em>(EUR)</em></td>
                                {selectedCountries.map(country => (<td key={country}>
                                    {formatCurrency(sumsPerCountry[country])}
                                </td>))}
                            </tr>
                            {pieCategoriesActive.map(category => (<tr key={category.name} style={{cursor:"pointer"}} onMouseEnter={() => setRowHighlightedCategory(category.name)} onMouseLeave={() => setRowHighlightedCategory(null)} onMouseUp={() => setSelectedCategory(category.name)}>
                                <td style={rowHighlightedCategory==category.name?{textAlign:"left",fontWeight:"bold",backgroundColor:"#EFEFEF"}:{textAlign:"left"}}>{category.name}</td>
                                {selectedCountries.map(country => (<td key={country} style={rowHighlightedCategory==category.name?{backgroundColor:"#EFEFEF"}:{}}>
                                    {formatCurrency(pieData[country][category.idx].sum)}
                                </td>))}
                            </tr>))}
                            <tr>
                                <td rowSpan="2" className="p-0 align-top">
                                    <div className="flex flex-col items-start px-4 pt-2 pb-2">
                                        {pieCategoriesActive.map(category => (
                                            <div key={category.name} style={{cursor:"pointer"}} className="flex items-center gap-1" onMouseEnter={() => setPieHighlightedCategory(category.name)} onMouseLeave={() => setPieHighlightedCategory(null)} onMouseUp={() => setSelectedCategory(category.name)}>
                                                <div 
                                                    className="w-4 h-4 rounded" 
                                                    style={{ backgroundColor: pieColors[category.idx] }}
                                                />
                                                <span
                                                    className="text-sm whitespace-nowrap inline-flex flex-col items-center after:content-[attr(data-text)] after:font-bold after:invisible after:h-0 after:block after:overflow-hidden"
                                                    style={pieHighlightedCategory===category.name?{"fontWeight":"bold"}:{}}
                                                    data-text={category.name}
                                                >{category.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </td>
                                {selectedCountries.map(country => (<td key={country} onMouseLeave={() => setPieHighlightedCategory(null)}>
                                    <BarChart
                                        data={pieData[country]}
                                        maxY={maxPerCountry}
                                        colors={pieColors}
                                        onBarEnter={setPieHighlightedCategory}
                                        onBarLeave={() => setPieHighlightedCategory(null)}
                                        onBarClick={c => setSelectedCategory(c)}
                                    />
                                </td>))}
                            </tr>
                            <tr>
                                {selectedCountries.map(country => (<td key={country} onMouseLeave={() => setPieHighlightedCategory(null)}>
                                    <PieChart
                                        data={pieData[country]}
                                        colors={pieColors}
                                        onPieEnter={setPieHighlightedCategory}
                                        onPieLeave={() => setPieHighlightedCategory(null)}
                                        onPieClick={c => setSelectedCategory(c)}
                                    />
                                </td>))}
                            </tr>
                        </tbody></table>
                    </div>
                </div>
            </section>)}

            {/* Items Breakdown Section */}
            {(selectedCountries.length > 0 && pieSum > 0 && !selectedCategory) && (<h1 className="mt-20 w-full text-center text-2xl font-semibold mb-20">Select a category to see items!</h1>)}
            {(selectedCountries.length > 0 && pieSum > 0 && selectedCategory) && (<section className="p-4">
                <div className="max-w-7xl mx-auto w-full">
                    <div className="overflow-auto pb-4">
                        <table className="table_compare_1 min-w-full" style={{tableLayout:"fixed"}}><tbody>
                            <tr className="table_compare_1_header_1"><td colSpan={selectedCountries.length*3}>{selectedCategory}</td></tr>
                            <tr className="table_compare_1_header_1">{selectedCountries.map(country => (<td key={country} colSpan={3}>{country}</td>))}</tr>
                            <tr className="table_compare_1_header_2">{selectedCountries.map(country => (<React.Fragment key={country}><td style={{width:`${100/selectedCountries.length}%`}}>name</td><td className="w-px">price</td><td className="w-px">vendor</td></React.Fragment>))}</tr>
                            {itemsActive.map(item => (<React.Fragment key={item}>
                                <tr>
                                    <td className="table_compare_1_category" colSpan={selectedCountries.length*3}>
                                        <CollapseButton isOpen={openedItems.includes(item)} onToggle={(isOpen) => {
                                            if (isOpen)
                                                setOpenedItems([...openedItems, item]);
                                            else
                                                setOpenedItems(openedItems.filter(cc => cc !== item));
                                        }}/>
                                        &nbsp;{item}
                                    </td>
                                </tr>
                                {(openedItems.includes(item)) &&
                                    [...Array(maxLinkCountPerItem[item])].map((_, idx) => (<tr key={idx}>
                                        {selectedCountries.map(country => (<React.Fragment key={country}>
                                            {(linksPerCountry[country][item].items.length > idx) ? (<React.Fragment>
                                                <td className="link_cell"><a className="item_link" target="_blank" href={linksPerCountry[country][item].items[idx].link}>{linksPerCountry[country][item].items[idx].name}</a></td>
                                                <td style={{"textAlign":"right"}}>{formatCurrency(linksPerCountry[country][item].items[idx].price)}</td>
                                                <td style={{"textAlign":"right"}}>{linksPerCountry[country][item].items[idx].vendor}</td>
                                            </React.Fragment>) : (<React.Fragment><td/><td/><td/></React.Fragment>)}
                                        </React.Fragment>))}
                                    </tr>))
                                }
                            </React.Fragment>))}
                        </tbody></table>
                    </div>
                </div>
            </section>)}

            {/* Footer */}
            <footer className="flex justify-between p-4 bg-gray-400">
                <div className="flex items-center space-x-9">
                    <p className="max-w-xs break-words text-xs text-justify">This site does not collect, store, or share any personal user data. We don't use cookies or trackers.</p>
                    <a target="_blank" href="https://github.com/nlevi-dev/PriceComparator?tab=Apache-2.0-1-ov-file">Apache-2.0 License</a>
                </div>
                <div className="flex items-center space-x-4">
                    <p>Contacts: </p>
                    <a target="_blank" href="https://github.com/nlevi-dev/PriceComparator">GitHub</a>
                    <a target="_blank" href="https://www.linkedin.com/in/nlevi-dev/">LinkedIn</a>
                </div>
            </footer>
           
        </div>
    );
}
export default App;