import requests
import time
import csv
import os
from datetime import datetime

INITIAL_INDEX_FILE = 'initial_index.csv'
LOG_FILE = 'crypto_index.csv'

def get_all_symbols():
    url = "https://api.bitkub.com/api/market/symbols"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        symbols = [item['symbol'] for item in data['result'] if item['symbol'].startswith('THB_')]
        return symbols
    else:
        print(f"Failed to fetch symbols. HTTP Status code: {response.status_code}")
        return None

def get_prices(symbols):
    url = "https://api.bitkub.com/api/market/ticker"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        prices = {}
        
        for symbol in symbols:
            price = data.get(symbol, {}).get("last")
            if price:
                prices[symbol] = price
            else:
                prices[symbol] = None
        
        return prices
    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
        return None

def calculate_index(prices):
    valid_prices = [price for price in prices.values() if price is not None]
    
    if valid_prices:
        index_value = sum(valid_prices) / len(valid_prices)
        return index_value
    else:
        print("No valid prices to calculate the index.")
        return None

def normalize_index(current_index, initial_index):
    normalized_value = (current_index / initial_index) * 100
    return normalized_value

def log_to_csv(filename, timestamp, normalized_index):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, normalized_index])

def load_initial_index():
    if os.path.exists(INITIAL_INDEX_FILE):
        with open(INITIAL_INDEX_FILE, mode='r') as f:
            reader = csv.reader(f)
            initial_value = next(reader)[0]
            return float(initial_value)
    else:
        return None

def save_initial_index(initial_value):
    with open(INITIAL_INDEX_FILE, mode='w') as f:
        writer = csv.writer(f)
        writer.writerow([initial_value])

if __name__ == '__main__':
    symbols = get_all_symbols()
    
    if symbols:
        print(f"Retrieved {len(symbols)} symbols.")

        initial_index = load_initial_index()
        
        if initial_index is None:
            initial_prices = get_prices(symbols)
            if initial_prices:
                initial_index = calculate_index(initial_prices)
                print(f"Initial Index Value (normalized to 100): 100.0")
                save_initial_index(initial_index)

                with open(LOG_FILE, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Normalized Index"])
            else:
                print("Could not retrieve initial prices. Exiting.")
                exit()

        print(f"Initial Index Value (loaded from file): {initial_index:.2f}")
        current_prices = get_prices(symbols)
        current_index = calculate_index(current_prices)
        print(f"Cuurent Index Value: {current_index:.2f} Change: {((current_index - initial_index) / initial_index ) * 100:.3f}%")
        while True:
            current_prices = get_prices(symbols)
            if current_prices:
                current_index = calculate_index(current_prices)
                
                if current_index is not None and initial_index is not None:
                    normalized_index = normalize_index(current_index, initial_index)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{timestamp} - Normalized Index Value: {normalized_index:.3f}")

                    log_to_csv(LOG_FILE, timestamp, normalized_index)

            time.sleep(1)
    else:
        print("Could not retrieve symbols. Exiting.")
