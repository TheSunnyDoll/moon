import requests
import time

url = "https://api.bitget.com/api/mix/v1/market/candles"
symbol = "BTCUSDT_UMCBL"
granularity = '1m'

# 获取当前时间戳和5小时前的时间戳
current_time = int(time.time())
start_time = current_time - (5 * 60 * 60)

params = {
    "symbol": symbol,
    "granularity": granularity,
    "startTime": start_time,
    "endTime": current_time
}

response = requests.get(url, params=params)
data = response.json()

if isinstance(data, list):
    candles = data

    swing_highs = []
    swing_lows = []

    for i in range(2, len(candles)):
        current_high = float(candles[i][2])
        prev_high = float(candles[i - 1][2])
        next_high = float(candles[i + 1][2])

        current_low = float(candles[i][3])
        prev_low = float(candles[i - 1][3])
        next_low = float(candles[i + 1][3])

        if current_high > prev_high and current_high > next_high:
            swing_highs.append((candles[i][0], current_high))
        elif current_low < prev_low and current_low < next_low:
            swing_lows.append((candles[i][0], current_low))

    print("Swing Highs:")
    for swing_high in swing_highs:
        print(f"Timestamp: {swing_high[0]}, Price: {swing_high[1]}")

    print("\nSwing Lows:")
    for swing_low in swing_lows:
        print(f"Timestamp: {swing_low[0]}, Price: {swing_low[1]}")
else:
    error_message = data["msg"]
    print(f"API请求错误：{error_message}")
