from utils import *
from pybitget import Client
import argparse

# Function to find pivot highs and pivot lows
def find_pivot_highs_lows(data, lookback):
    pivot_highs = []
    pivot_lows = []

    for i in range(lookback, len(data) - lookback):
        if all(data[i] > data[i - lookback:i]) and all(data[i] >= data[i + 1:i + lookback + 1]):
            pivot_highs.append((i, data[i]))
        elif all(data[i] < data[i - lookback:i]) and all(data[i] <= data[i + 1:i + lookback + 1]):
            pivot_lows.append((i, data[i]))

    return pivot_highs, pivot_lows

# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username')

args = parser.parse_args()
heroname = args.username

# Get API credentials from the configuration file
config = get_config_file()
hero = config[heroname]
symbol = 'BTCUSDT_UMCBL'
huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])

# Get the timestamps for the desired data range
startTime = get_previous_three_hour_timestamp()
endTime = get_previous_minute_timestamp()

# Retrieve BTC 3-hour 15-minute candlestick data
data = huFu.mix_get_candles(symbol, '15m', startTime, endTime)

print(data['data'])
# Extract the 'close' prices from the data
close_prices = [float(item['close']) for item in data['data']]

# Set the lookback value for finding pivot highs and pivot lows
lookback = 5

# Find pivot highs and pivot lows in the close prices data
pivot_highs, pivot_lows = find_pivot_highs_lows(close_prices, lookback)

# Print pivot highs and pivot lows
print("Pivot Highs:")
for high in pivot_highs:
    print(f"Index: {high[0]}, Value: {high[1]}")

print("\nPivot Lows:")
for low in pivot_lows:
    print(f"Index: {low[0]}, Value: {low[1]}")
