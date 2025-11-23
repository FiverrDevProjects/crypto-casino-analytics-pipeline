````markdown
# Crypto Gaming Data Pipeline

This repository contains a Python pipeline for processing, cleaning, and analyzing gaming data with cryptocurrency transactions. It extracts data from `.rar` archives, merges JSON files, enriches them with historical crypto prices, classifies games, calculates USD amounts, and generates summary analytics in both CSV and Excel formats.

---

## Features

- **Extract `.rar` files** using [unar](https://theunarchiver.com/command-line)
- **Merge multiple JSON files** into a single structured dataset
- **Flatten nested JSON structures**
- **Fetch historical cryptocurrency prices** using the CryptoCompare API
- **Calculate USD amounts** for bets and payouts
- **Classify games** into categories: slot, crash, sports, live, instant, and other casino games
- **Generate CSV output** with cleaned data
- **Generate Excel analytics** including:
  - Overall summary
  - Slot vs Sports summary
  - Breakdown by game type
  - Cryptocurrency prices by date

---

## Requirements

- Python 3.9+
- Dependencies (install via `pip`):

```bash
pip install pandas requests xlsxwriter
````

* [unar](https://theunarchiver.com/command-line) (command-line tool to extract `.rar` archives)

---

## Project Structure

```
.
├── complete_data.rar             # Source RAR archive with JSON files
├── complete_data_extracted/      # Folder where JSON files will be extracted
├── crypto_price_cache.json       # Cache for previously fetched crypto prices
├── cleaned_data_with_crypto.csv  # Final cleaned CSV output
├── analytics.xlsx                # Excel summary output
├── main.py                       # Main pipeline script
└── README.md and requirements.txt
```

---

## Usage

1. **Place your `.rar` archive** (`complete_data.rar`) in the root directory.
2. **Ensure `unar` is installed** and available in your system PATH.
3. **Run the pipeline**:

```bash
python main.py
```

4. **Outputs generated**:

* `cleaned_data_with_crypto.csv` → merged, flattened, and enriched data
* `analytics.xlsx` → summary analytics and coin price history
* `crypto_price_cache.json` → cached crypto prices to avoid redundant API calls

---

## Configuration

* **Paths** (relative to `main.py`) can be modified in the script:

```python
RAR_PATH   = os.path.join(BASE_DIR, "complete_data.rar")
EXTRACT_TO = os.path.join(BASE_DIR, "complete_data_extracted")
OUTPUT_CSV = os.path.join(BASE_DIR, "cleaned_data_with_crypto.csv")
CACHE_PATH = os.path.join(BASE_DIR, "crypto_price_cache.json")
```

* **API URL**:

```python
API_URL = "https://min-api.cryptocompare.com/data/v2/histoday"
```

---

## Notes

* The pipeline **caches cryptocurrency prices** locally to minimize API calls and speed up processing.
* Betting types are automatically classified based on `game`, `gameName`, and `type`.
* If the `payoutMultiplier` is 0 or missing, `payout_usd` defaults to the original bet amount in USD.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

* [CryptoCompare API](https://min-api.cryptocompare.com/) for historical cryptocurrency data
* [The Unarchiver](https://theunarchiver.com/command-line) for `.rar` extraction
* [pandas](https://pandas.pydata.org/) for data manipulation

```


