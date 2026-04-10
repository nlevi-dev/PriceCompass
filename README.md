# Price Compass
**Empowering international price transparency through open data.**

Price Compass is an open-source tool designed to provide a granular, verifiable look at the cost of living across borders. Unlike traditional cost-of-living indexes that offer "black box" metrics, Price Compass serves both aggregated insights and the underlying raw data, allowing users to verify, audit, and calculate their own economic indicators.

## Key Features

- **Custom "Shopping Baskets":** Define your own lifestyle. Instead of generic averages, build a monthly cart reflecting what *you* actually consume (e.g., 10L milk, 2 gym memberships, 1 monthly transit pass).
- **Radical Transparency:** Access the raw, non-aggregated data points. Every price is tagged with a vendor name, timestamp and a link to the product.
- **On-the-Fly Aggregation:** Switch between aggregation modes such as `Average`, `Minimum`, or `Maximum` to instantly see the full market spectrum.
- **Privacy-First Architecture:** Zero Cookies & Zero Trackers.
- **URL State Management:** Your entire dashboard configuration and comparison are stored in the URL hash. Share your findings just by copying the link.
- **Static & Efficient:** The frontend is a static page with the latest daily data baked in, ensuring high performance and low overhead.

## Data Philosophy & Ethics

We believe in being responsible citizens of the web while democratizing economic information.

1.  **Polite Scraping:** Our engine strictly adheres to `robots.txt` and uses aggressive caching during development and production to minimize server load on source retailers.
2.  **Limited Catalog:** We only track a curated subset of essential "indicator" goods (e.g., milk, eggs, bread) to provide a snapshot of purchasing power without infringing on the commercial value of a retailer's full catalog.
3.  **Nominative Use:** Vendor names (e.g., Tesco, Aldi) are used solely for data attribution and origin transparency. No trademarks or logos are used.
4.  **Open Access:** All scraped data is available for download, allowing researchers and hobbyists to challenge or verify official statistics.

## Legal & Compliance

This project is built with a commitment to legal transparency and open-source standards.

- **Third-Party Data:** Price Compass serves as a tool for aggregating publicly available information. We do not claim ownership of the underlying price data sourced from third-party vendors.
- **Licenses & Notices:** For a comprehensive list of licenses, dependencies, and data source attributions, please refer to our **[THIRD-PARTY-NOTICES.md](https://github.com/nlevi-dev/PriceCompass/tree/master/THIRD-PARTY-NOTICES.md)**.
- **Notice to Vendors & Legal Representatives:** We aim to be a "polite" consumer of public data. If you are a representative of a vendor indexed here and believe our automated collection is in breach of your Terms of Service or specific data policies, please reach out directly via [LinkedIn](https://www.linkedin.com/in/nlevi-dev/) or open a GitHub Issue. We are committed to resolving concerns regarding data usage or crawler behavior promptly and amicably.
- **User Responsibility & Liability:** This software is provided "as is." If you choose to clone this repository and execute the scraping scripts yourself, you do so at your own risk. Price Compass and its contributors are not held liable for any breaches of Terms of Service (ToS), IP bans, or legal consequences resulting from your independent use of these tools. It is your responsibility to ensure your scraping activities comply with local laws and target website policies.
- **Disclaimer:** *Price Compass is an experimental, open-source project provided for informational and educational purposes only. Data is scraped from public websites; while we strive for accuracy, we cannot guarantee the real-time precision of prices. This tool is not financial advice and should not be used as the sole basis for major economic decisions.*