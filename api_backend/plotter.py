import asyncio
import aiohttp
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend, which doesn't require a GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone, timedelta
import os
from typing import Dict, Any
import time
from functools import lru_cache

# Constants
ALL_TOKENS = ["BTC", "ETH", "SOL", "JUP", "SHDW", "JTO", "WIF", "BONK"]
RESOLUTIONS = {
    '15m': {'resolution': '15', 'days': 2},
    '1h': {'resolution': '60', 'days': 7},
    '4h': {'resolution': '240', 'days': 21},
    '1d': {'resolution': 'D', 'days': 120},
    '1w': {'resolution': 'W', 'days': 360}
}
OUTPUT_DIR = "graphs"
HOSTING_BASE_URL = "https://shdw-drive.genesysgo.net/3UgjUKQ1CAeaecg5CWk88q9jGHg8LJg9MAybp4pevtFz/"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

@lru_cache(maxsize=100)
async def fetch_historical_data(session: aiohttp.ClientSession, symbol: str, resolution: str, days_back: int) -> Dict[str, Any]:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)
    from_timestamp = int(start_time.timestamp())
    to_timestamp = int(end_time.timestamp())
    
    url = "https://benchmarks.pyth.network/v1/shims/tradingview/history"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_timestamp,
        "to": to_timestamp
    }
    
    headers = {'accept': 'application/json'}
    start_request_time = time.time()
    
    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                end_request_time = time.time()
                print(f"Fetching data for {symbol} ({resolution}) took {end_request_time - start_request_time} seconds")
                
                if data['s'] == 'ok' and data['t']:
                    return {
                        'datetime': np.array([datetime.fromtimestamp(ts, tz=timezone.utc) for ts in data['t']]),
                        'open': np.array(data['o']),
                        'high': np.array(data['h']),
                        'low': np.array(data['l']),
                        'close': np.array(data['c']),
                        'volume': np.array(data['v'])
                    }
                else:
                    print(f"Data fetch was successful but returned an empty dataset for {symbol} ({resolution})")
                    return {}
            else:
                print(f"Failed to fetch data for {symbol} ({resolution}): {response.status}, Response: {await response.text()}")
                return {}
    except Exception as e:
        print(f"Error fetching data for {symbol} ({resolution}): {str(e)}")
        return {}

def calculate_bollinger_bands(data, window=20, num_std=2):
    rolling_mean = np.convolve(data, np.ones(window), 'valid') / window
    rolling_std = np.array([np.std(data[i:i+window]) for i in range(len(data)-window+1)])
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band

def find_local_extrema(data, window=6):
    if len(data) < 2 * window + 1:
        return [], []  # Return empty lists if the data is too short

    highs = []
    lows = []
    for i in range(window, len(data) - window):
        if np.all(data[i] > data[i-window:i]) and np.all(data[i] > data[i+1:i+window+1]):
            highs.append(i)
        if np.all(data[i] < data[i-window:i]) and np.all(data[i] < data[i+1:i+window+1]):
            lows.append(i)
    return np.array(highs, dtype=int), np.array(lows, dtype=int)

def consolidate_levels(levels, tolerance=0.02):
    if len(levels) == 0:  # Check if the list is empty
        return []  # Return an empty list if no levels are found
    
    sorted_levels = np.sort(levels)
    consolidated = []
    current_group = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        if (level - current_group[-1]) / current_group[-1] <= tolerance:
            current_group.append(level)
        else:
            consolidated.append((np.mean(current_group), len(current_group)))
            current_group = [level]
    
    consolidated.append((np.mean(current_group), len(current_group)))
    return consolidated

def plot_candles(historical_data: Dict[str, Any], symbol: str, interval: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 6))
    
    dates = historical_data['datetime']
    close_prices = historical_data['close']
    
    # Calculate Bollinger Bands for the entire dataset
    bb_window = min(20, len(close_prices))
    middle_band, upper_band, lower_band = calculate_bollinger_bands(close_prices, window=bb_window)
    
    # Find local highs and lows
    local_highs, local_lows = find_local_extrema(close_prices, window=5)
    
    # Plot candlesticks
    for i in range(len(dates)):
        date = dates[i]
        open_price = historical_data['open'][i]
        high_price = historical_data['high'][i]
        low_price = historical_data['low'][i]
        close_price = close_prices[i]
        
        color = 'limegreen' if close_price >= open_price else 'crimson'
        ax.plot([date, date], [low_price, high_price], color=color)
        ax.plot([date, date], [open_price, close_price], color=color, linewidth=5)
    
    # Plot Bollinger Bands
    bb_dates = dates[bb_window-1:]
    ax.plot(bb_dates, middle_band, color='blue', linestyle='--', label='Middle Band')
    ax.plot(bb_dates, upper_band, color='gray', linestyle=':', label='Upper Band')
    ax.plot(bb_dates, lower_band, color='gray', linestyle=':', label='Lower Band')
    
    # Plot local highs and lows
    if len(local_highs) > 0:
        ax.scatter(dates[local_highs], close_prices[local_highs], color='red', marker='^', s=100, label='Local High')
    if len(local_lows) > 0:
        ax.scatter(dates[local_lows], close_prices[local_lows], color='green', marker='v', s=100, label='Local Low')
    
    # Consolidate and plot horizontal lines
    high_levels = consolidate_levels(close_prices[local_highs])
    low_levels = consolidate_levels(close_prices[local_lows])

    for level, count in high_levels:
        ax.axhline(y=level, color='red', linestyle='--', alpha=0.5, linewidth=count)
    for level, count in low_levels:
        ax.axhline(y=level, color='green', linestyle='--', alpha=0.5, linewidth=count)
    
    ax.set_title(f"{symbol} {interval} Candles with Bollinger Bands and Key Levels", fontsize=15)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Format x-axis to show dates nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    fig.autofmt_xdate()
    plt.tight_layout()
    
    # Save the plot
    filename = f"{interval}_{symbol.replace('/', '_')}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100)
    plt.close(fig)
    
    return filename

async def fetch_and_plot_data(session: aiohttp.ClientSession):
    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent tasks

    async def fetch_and_plot(token, interval, resolution_info):
        async with semaphore:
            symbol = f"Crypto.{token}/USD"
            try:
                data = await fetch_historical_data(session, symbol, resolution_info['resolution'], resolution_info['days'])
                if data:
                    filename = plot_candles(data, symbol, interval)
                    print(f"Saved plot: {filename}")
                else:
                    print(f"No data available for {symbol} - {interval}")
            except Exception as e:
                print(f"Error processing {symbol} - {interval}: {str(e)}")

    tasks = [
        fetch_and_plot(token, interval, resolution_info)
        for token in ALL_TOKENS
        for interval, resolution_info in RESOLUTIONS.items()
    ]

    await asyncio.gather(*tasks)

async def main():
    async with aiohttp.ClientSession() as session:
        await fetch_and_plot_data(session)

if __name__ == "__main__":
    asyncio.run(main())