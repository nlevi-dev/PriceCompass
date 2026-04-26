import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import requests
from datetime import datetime

from scrapers.types import Currency

class CurrencyExchanger:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.cache_file = self.base_dir / "cache" / "exchange_rates.json"
        self.cache_file.parent.mkdir(exist_ok=True)
        self.api_url = "https://api.frankfurter.dev/v1/latest?base={base}&symbols={quote}"
        self._cache = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self._cache, f, indent=4)

    def get_exchange_rate(self, from_currency, to_currency):
        if isinstance(from_currency, Currency):
            from_currency = from_currency.name
        if isinstance(to_currency, Currency):
            to_currency = to_currency.name
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"{current_date}_{from_currency}_{to_currency}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        url = self.api_url.format(base=from_currency, quote=to_currency)
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        rate = data["rates"][to_currency]
        
        if rate is None:
            raise ValueError(f"Could not find rate for {to_currency}")

        self._cache[cache_key] = rate
        self._save_cache()
        
        return rate

if __name__ == "__main__":
    exchanger = CurrencyExchanger()
    print(f"Rate 1: {exchanger.get_exchange_rate('HUF', 'EUR')}")
    print(f"Rate 2: {exchanger.get_exchange_rate('HUF', 'EUR')}")