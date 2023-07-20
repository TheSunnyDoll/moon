import numpy as np
from math import floor
from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *

def zigzag(*, klines, min_size, percent):
    klines = np.array(object=klines, dtype=np.float64)
    time = klines[:, 0]
    high = klines[:, 2]
    low = klines[:, 3]
  
    length = len(klines)
    zigzag = np.zeros(length)
    trend, last_high, last_low = 0, 0, 0
    
    for i in range(length):
        if trend == 0:
            price_change = min_size * (low[0] if percent else 1)
            if high[i] >= low[0] + price_change:
                trend = 1
                last_high = i
                zigzag[0] = -1
                continue
            price_change = min_size * (high[0] if percent else 1)
            if low[i] <= high[0] - price_change:
                trend = -1
                last_low = i
                zigzag[0] = 1

        if trend == 1:
            price_change = min_size
            if percent:
                price_change *= high[last_high]
            exp = low[i] <= high[last_high] - price_change
            if exp and high[i] < high[last_high]:
                trend = -1
                zigzag[last_high] = 1
                last_low = i
            if high[i] > high[last_high]:
                last_high = i

        if trend == -1:
            price_change = min_size
            if percent:
                price_change *= low[last_low]
            exp = high[i] >= low[last_low] + price_change
            if exp and low[i] > low[last_low]:
                trend = 1
                zigzag[last_low] = -1
                last_high = i
            if low[i] < low[last_low]:
                last_low = i

    last_trend = 0
    last_trend_index = 0

    for i in range(length - 1, -1, -1):
        if zigzag[i] != 0:
            last_trend = zigzag[i]
            last_trend_index = i
            break

    determinant = 0
    high_determinant = high[last_trend_index]
    low_determinant = low[last_trend_index]

    for i in range(last_trend_index + 1, length):
        if last_trend == 1 and low[i] < low_determinant:
            low_determinant = low[i]
            determinant = i

        if last_trend == -1 and high[i] > high_determinant:
            high_determinant = high[i]
            determinant = i

    if last_trend == 1:
        zigzag[determinant] = -1
    if last_trend == -1:
        zigzag[determinant] = 1

    out = []

    for i in range(length):
        if zigzag[i] == 1:
            out.append([time[i], high[i]])
        if zigzag[i] == -1:
            out.append([time[i], low[i]])
    sorted_price = sorted(out, key=lambda x: x[0])
    price = [item[1] for item in sorted_price]

    ### 小周期
    # 创建空列表用于存储结果
    result = []
    # 循环遍历每两个值进行比较，并添加相应的标签和两个值组成子列表
    for i in range(1, len(price)):
        if price[i] > price[i - 1]:
            result.append(['bull', price[i - 1], price[i]])
        else:
            result.append(['bear', price[i - 1], price[i]])
    ### 大周期
    # 创建一个新的空列表用于存储结果
    big_trend = []

    # 初始化变量用于记录最低值和最高值的索引
    low_index = 0
    high_index = 0

    # 循环遍历列表，找到最低值和最高值的索引
    for i in range(1, len(price)):
        if price[i] < price[low_index]:
            low_index = i
        if price[i] > price[high_index]:
            high_index = i

    # 判断最低值和最高值的先后出现顺序，并添加标签和对应的值到结果列表
    if low_index < high_index:
        big_trend.append(['bull', price[low_index], price[high_index]])
        # 将price列表按大小排序，取倒数第二低的值
        price_sorted = sorted(price)
        big_trend[0].append(price_sorted[1])
    else:
        big_trend.append(['bear', price[high_index], price[low_index]])
        # 将price列表按大小排序，取第二高的值
        price_sorted = sorted(price, reverse=True)
        big_trend[0].append(price_sorted[1])

    return result,big_trend

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username')

args = parser.parse_args()
heroname = args.username

config = get_config_file()
hero = config[heroname]
symbol = 'BTCUSDT_UMCBL'
huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
startTime = get_previous_month_timestamp()
endTime = get_previous_minute_timestamp()
klines = huFu.mix_get_candles(symbol, '15m', startTime, endTime)

r,b = zigzag(klines=klines, min_size=0.0055, percent=True)
print(r)
print(f'15m 级别趋势,{b}')

klines = huFu.mix_get_candles(symbol, '30m', startTime, endTime)

r,b = zigzag(klines=klines, min_size=0.0055, percent=True)
print(f'30m 级别趋势,{b}')

klines = huFu.mix_get_candles(symbol, '1H', startTime, endTime)

r,b = zigzag(klines=klines, min_size=0.0055, percent=True)
print(f'1H 级别趋势,{b}')