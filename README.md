
# Crypto Gaming Data Pipeline

This repository contains a Python pipeline for processing, cleaning, and analyzing gaming data with cryptocurrency transactions. It extracts data from `.rar` archives, merges JSON files, improves them with historical crypto prices, classifies games, calculates USD amounts, and generates summary analytics in both CSV and Excel formats.

---

## Features

- Extract `.rar` files using [unar](https://theunarchiver.com/command-line)
- Merge multiple JSON files into a single structured dataset
- Flatten nested JSON structures
- Fetch historical cryptocurrency prices using the CryptoCompare API
- Calculate USD amounts for bets and payouts
- Classify games into categories: slot, crash, sports, live, instant, and other casino games
- Generate CSV output with cleaned data
- Generate Excel analytics including:
  - Overall summary
  - Slot vs Sports summary
  - Breakdown by game type
  - Cryptocurrency prices by date

---

## Requirements

- Python 3.9+
- Dependencies (install via pip):

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


### **macOS**

1. **Using Homebrew (recommended):**

```bash
brew install unar
```

2. **Verify installation:**

```bash
unar -V
```

You should see the version printed.

3. **If `unar` is not found:**

   * Make sure Homebrew’s bin directory is in your PATH:

```bash
export PATH="/usr/local/bin:$PATH"
```

You can add the above line to your `~/.zshrc` or `~/.bash_profile` to make it permanent.

---

### **Windows**

1. **Download Unarchiver for Windows:**

   * Go to [https://theunarchiver.com/command-line](https://theunarchiver.com/command-line) and download the Windows version.

2. **Extract `unar.exe`** to a folder, e.g., `C:\Program Files\unar\`.

3. **Add folder to PATH:**

   * Press `Win + S`, search for **Environment Variables**, and open **Edit the system environment variables**.
   * Click **Environment Variables…**
   * Under **System variables**, select `Path` -> **Edit…**
   * Click **New** and add the folder path where `unar.exe` is located (e.g., `C:\Program Files\unar\`).
   * Click **OK** to save.

4. **Verify installation:**

```cmd
unar -V
```




---

1. Place your `.rar` archive (`complete_data.rar`) in the root directory.
2. Ensure `unar` is installed and available in your system PATH.
3. Run the pipeline:

```bash
python main.py
```

**Outputs generated:**

* `cleaned_data_with_crypto.csv` - merged, flattened, and enriched data
* `analytics.xlsx` - summary analytics and coin price history
* `crypto_price_cache.json` -
cached crypto prices to avoid redundant API calls

---

## Configuration

Paths (relative to `main.py`) can be modified in the script:

```python
RAR_PATH   = os.path.join(BASE_DIR, "complete_data.rar")
EXTRACT_TO = os.path.join(BASE_DIR, "complete_data_extracted")
OUTPUT_CSV = os.path.join(BASE_DIR, "cleaned_data_with_crypto.csv")
CACHE_PATH = os.path.join(BASE_DIR, "crypto_price_cache.json")

API_URL = "https://min-api.cryptocompare.com/data/v2/histoday"
```

---

## Notes

* The pipeline caches cryptocurrency prices locally to minimize API calls and speed up processing.
* Betting types are automatically classified based on `game`, `gameName`, and `type`.
* If the `payoutMultiplier` is 0 or missing, `payout_usd` defaults to the original bet amount in USD.

---


---

## For Collaborators

To use this project:

1. **Clone the repository**  

   Using SSH (recommended if you have access via deploy key):
   ```bash
   git clone git@github.com:FiverrDevProjects/crypto-casino-analytics-pipeline.git

Or using HTTPS (requires GitHub login and personal access token for private repos):

```bash
git clone https://github.com/FiverrDevProjects/crypto-casino-analytics-pipeline.git
```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Add the `.rar` file**
   Place your `complete_data.rar` archive in the root directory of the cloned repo.

4. **Run the pipeline**:

   ```bash
   python main.py
   ```

5. **Outputs**:

   * `cleaned_data_with_crypto.csv` → cleaned and merged data
   * `analytics.xlsx` → Excel summary analytics
   * `crypto_price_cache.json` → cached crypto prices

> Note: Generated files are **not included** in the repository. Each collaborator generates them locally after running the pipeline.




---

## License

Copyright (c) 2025 @analytix_pro

---

## Acknowledgements

* [CryptoCompare API](https://min-api.cryptocompare.com/) for historical cryptocurrency data
* [The Unarchiver](https://theunarchiver.com/command-line) for `.rar` extraction
* [pandas](https://pandas.pydata.org/) for data manipulation






