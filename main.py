from datetime import datetime
import os
import sys
import shutil
import subprocess
import json
import pandas as pd
import requests
from datetime import datetime, timezone

# ------ BASE ----------------
# ---------------- PATH FIX FOR EXE ----------------
# Determine base directory
if getattr(sys, 'frozen', False):
    # Running inside PyInstaller bundle
    BASE_DIR = sys._MEIPASS
    # Output should go where the EXE is launched from
    RUNTIME_DIR = os.getcwd()
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUNTIME_DIR = BASE_DIR

# Input .rar stays next to script/exe
RAR_PATH   = os.path.join(RUNTIME_DIR, "complete_data.rar")

# Extraction/output go in runtime folder (not inside _MEIPASS)
EXTRACT_TO = os.path.join(RUNTIME_DIR, "complete_data_extracted")
OUTPUT_CSV = os.path.join(RUNTIME_DIR, "cleaned_data_with_crypto.csv")
CACHE_PATH = os.path.join(RUNTIME_DIR, "crypto_price_cache.json")

# unar.exe must be bundled manually with PyInstaller
UNAR_PATH = os.path.join(BASE_DIR, "unar.exe")

# Check if unar.exe exists
if not os.path.exists(UNAR_PATH):
    # Try PATH if user has installed it manually
    fallback = shutil.which("unar")
    if fallback:
        UNAR_PATH = fallback
    else:
        raise FileNotFoundError(
            "unar.exe not found.\n"
            "Place unar.exe next to the script/exe or install UNAR CLI."
        )

print(f"Repo base dir (bundle): {BASE_DIR}")
print(f"Working/output dir: {RUNTIME_DIR}")
print(f"RAR path: {RAR_PATH}")
print(f"Extraction folder: {EXTRACT_TO}")
print(f"Output CSV: {OUTPUT_CSV}")
print(f"Cache path: {CACHE_PATH}")
print(f"Using unar at: {UNAR_PATH}")

# re-create extraction folder if missing
os.makedirs(EXTRACT_TO, exist_ok=True)

# ---------------- END PATH FIX ----------------


# -------- TOOLS ----------------

#  API for updating historical cripto prices
API_URL = "https://min-api.cryptocompare.com/data/v2/histoday"

# ----------------
print(f"Repo base dir: {BASE_DIR}")
print(f"RAR path: {RAR_PATH}")
print(f"Extraction folder: {EXTRACT_TO}")
print(f"Output CSV: {OUTPUT_CSV}")
print(f"Cache path: {CACHE_PATH}")
print(f"unar path: {UNAR_PATH}")

# ------------------

def extract_rar(rar_path, extract_to):
    # Remove the old folder if it exists
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
        print(f"Removed old extraction folder: {extract_to}")

    # Re-create folder and extract
    os.makedirs(extract_to, exist_ok=True)
    print(f"Extracting {rar_path} to {extract_to}...")
    subprocess.run([UNAR_PATH, "-o", extract_to, rar_path], check=True,
               stdout=subprocess.DEVNULL)
    print("Extraction complete.")


def find_json_files(folder):
    json_files = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))
    return json_files
    
#--------merging all files---------------
def merge_json_files(file_list):
    merged_data = []
    for path in file_list:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                merged_data.append(data)
    return merged_data

def flatten_record(entry):
    flat_entry = entry.copy()
    state = flat_entry.pop('statePlinko', {})
    for key, value in state.items():
        if isinstance(value, list):
            flat_entry[f'statePlinko_{key}'] = ','.join(map(str, value))
        else:
            flat_entry[f'statePlinko_{key}'] = value
    return flat_entry

# -------------temporary storage-cache the results ----
def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            raw = json.load(f)
            return {(s, datetime.strptime(d, "%Y-%m-%d").date()): v for s, d, v in raw}
    return {}

def save_cache(cache):
    cache_list = [(s, d.strftime("%Y-%m-%d"), v) for (s, d), v in cache.items()]
    with open(CACHE_PATH, "w") as f:
        json.dump(cache_list, f, indent=2)

# ---- cripto API -fetching -historical-price--------------

def fetch_crypto_prices(symbol, dates, cache):
    to_fetch = [d for d in dates if (symbol, d) not in cache]
    if not to_fetch:
        return cache

    start = min(to_fetch)
    end = max(to_fetch)
    limit = (end - start).days + 1
    ts_end = int(pd.Timestamp(end).timestamp())
    params = {"fsym": symbol.upper(), "tsym": "USD", "toTs": ts_end, "limit": limit}

    try:
        r = requests.get(API_URL, params=params).json()
        data = r["Data"]["Data"]
        for candle in data:
            # timezone replacement
            date = datetime.fromtimestamp(candle["time"], tz=timezone.utc).date()
            if date in to_fetch:
                cache[(symbol, date)] = candle["close"]
    except Exception as e:
        for d in to_fetch:
            cache[(symbol, d)] = None
    return cache


# -------classify--------------
def get_vertical(df):
    df['game_lower'] = df['game'].fillna('').str.lower()
    df['type_lower'] = df['type'].fillna('').str.lower()
    df['gameName_lower'] = df['gameName'].fillna('').str.lower()

    slot_keywords = ["slot", "reels", "megaways", "bonanza", "fruit", "spins", "jackpot"]
    known_slots = ["sugar", "wanted", "olympus", "dog house", "starlight",
                   "gates", "madame destiny", "big bass", "book of", "chaos crew"]

    def classify_row(row):
        g = row['game_lower']
        gn = row['gameName_lower']
        t = row['type_lower']

        if t == "sportsbook":
            return "sports"
        if g in ["crash", "plinko", "slide", "tower"]:
            return "crash"
        if g in ["mines", "dice", "limbo", "hilo", "keno", "wheel"]:
            return "instant"
        if t == "evolution":
            return "live"
        if any(k in gn for k in slot_keywords) or any(k in known_slots for k in known_slots):
            return "slot"
        return "casino_other"

    df['betting'] = df.apply(classify_row, axis=1)
    df.drop(columns=['game_lower', 'gameName_lower', 'type_lower'], inplace=True)
    return df


# ---------------- main ----------------
# ---------------- main ----------------
def main():
    # 1. Check if .rar exists
    if os.path.exists(RAR_PATH):
        print(f"Found RAR: {RAR_PATH}, extracting...")
        extract_rar(RAR_PATH, EXTRACT_TO)
    else:
        print(f"No RAR found, using existing folder: {EXTRACT_TO}")
        if not os.path.exists(EXTRACT_TO):
            raise FileNotFoundError(
                f"No RAR and no extracted folder found at {EXTRACT_TO}"
            )

    # 2. Find JSON files
    json_files = find_json_files(EXTRACT_TO)
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {EXTRACT_TO}")
    
    print(f"Found {len(json_files)} JSON files. Proceeding with merging...")

    # 3. Merging json files
    merged_data = merge_json_files(json_files)

    # 4. Flattening records
    flattened = [flatten_record(entry) for entry in merged_data]
    df = pd.DataFrame(flattened)

    # 5. Convert timestamps to date
    df['createdAt_dt'] = pd.to_datetime(df['createdAt'], unit='ms', errors='coerce')
    df['createdAt_date'] = df['createdAt_dt'].dt.date

    # 6. load cached results
    cache = load_cache()

    # 7. get prices per unique currency
    unique_currencies = df['currency'].dropna().unique()
    for cur in unique_currencies:
        dates = df.loc[df['currency']==cur, 'createdAt_date'].dropna().unique()
        cache = fetch_crypto_prices(cur, dates, cache)

    # 8. Map the price to dataframe
    df['price_usd'] = df.apply(lambda row: cache.get((row['currency'], row['createdAt_date'])), axis=1)

    # 9. Calculate USD amounts
    if 'amount' in df.columns:
        df['amount_usd'] = df['amount'] * df['price_usd']

    # 10. payout_usd calculation
    df['payout_usd'] = df.apply(
        lambda row: row['payout'] * row['price_usd']
        if row.get('payoutMultiplier', 0) > 0 and row.get('payout', 0) > 0
        else row['amount_usd'],
        axis=1
    )

    # 11. classify 
    df_filtered = get_vertical(df)
    df_filtered['game'] = df_filtered['game'].fillna(df['type'])
    
    df_filtered = df_filtered[['game','type','value','amount','payout','currency',
                               'expectedAmount','payoutMultiplier','createdAt_dt',
                               'createdAt_date','price_usd','amount_usd','payout_usd','betting']]

    # 12. Adjust betting for certain types
    df_filtered.loc[df_filtered['type'].isin(['softswiss','thirdparty']), 'betting'] = 'slot'
    df_filtered = df_filtered.copy()
    df_filtered['expectedAmount'] = df_filtered['expectedAmount'].astype(float)

    # 13. Save 
    df_filtered.to_csv(OUTPUT_CSV, index=False)
    print(f"Pipeline complete! CSV saved: {OUTPUT_CSV}")

    # 14. Save cache
    save_cache(cache)

    # ---------------- SUMMARY ----------------
    df_filtered['payout_usd'] = df_filtered.apply(
        lambda row: row['payout']*row['price_usd'] if row['payoutMultiplier'] > 0 else row['amount_usd'],
        axis=1
    )

    # overall summary
    overall_summary = pd.DataFrame([{
        "Total Bet (USD)": df_filtered['amount_usd'].sum(),
        "Total Payout (USD)": df_filtered['payout_usd'].sum(),
        "Net Profit (USD)": df_filtered['amount_usd'].sum() - df_filtered['payout_usd'].sum()
    }])

    # slot vs sports summary
    slot_sports_summary = (
        df_filtered[df_filtered['betting'].isin(['slot','sports'])]
        .groupby('betting')
        .agg(amount_usd=('amount_usd','sum'),
             payout_usd=('payout_usd','sum'))
        .reset_index()
    )

    # type
    breakdown_by_type = (
        df_filtered.groupby('type')
        .agg(amount_usd=('amount_usd','sum'),
             payout_usd=('payout_usd','sum'))
        .reset_index()
    )

    # single summary sheet
    summary_rows = []
    summary_rows.append(["Overall summary"])
    summary_rows.append(overall_summary.columns.tolist())
    summary_rows.extend(overall_summary.values.tolist())
    summary_rows.append([])
    summary_rows.append(["Slot vs Sports"])
    summary_rows.append(slot_sports_summary.columns.tolist())
    summary_rows.extend(slot_sports_summary.values.tolist())
    summary_rows.append([])
    summary_rows.append(["Breakdown by game"])
    summary_rows.append(breakdown_by_type.columns.tolist())
    summary_rows.extend(breakdown_by_type.values.tolist())

    summary_sheet = pd.DataFrame(summary_rows)

    # coin prices sheet
    coin_price_rows = []
    for (symbol, date), price in cache.items():
        coin_price_rows.append({
            "currency": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "price_usd": price
        })
    coin_prices_by_date = pd.DataFrame(coin_price_rows)

    # excel path in runtime folder
    excel_path = os.path.join(RUNTIME_DIR, "analytics.xlsx")
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        summary_sheet.to_excel(writer, sheet_name="summary", index=False, header=False)
        df_filtered.to_excel(writer, sheet_name="main_data", index=False)
        coin_prices_by_date.to_excel(writer, sheet_name="coin_prices_by_date", index=False)

    print(f"Analytics Excel created: {excel_path}")


if __name__ == "__main__":
    main()
