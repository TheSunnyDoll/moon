from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *

# 之前实现的 ZigZag 函数
def zigzag(high, low, depth=12, deviation=5, backstep=2):
    # 返回 ZigZag 高低点的 DataFrame
    lw = 1
    hg = 1
    last_h = 1
    last_l = 1
    p_lw = -np.inf
    p_hg = -np.inf
    lw_vals = []
    hg_vals = []
    
    for i in range(len(high)):
        lw = lw + 1
        hg = hg + 1
        p_lw = max(p_lw, i - depth)
        p_hg = max(p_hg, i - depth)
        
        lowing = lw == p_lw or low[i] - low[p_lw] > deviation * np.min(np.diff(low))
        highing = hg == p_hg or high[p_hg] - high[i] > deviation * np.min(np.diff(high))
        
        lh = 0 if highing else lh + 1
        ll = 0 if lowing else ll + 1
        down = lh >= backstep
        lower = low[i] > low[p_lw]
        higher = high[i] < high[p_hg]
        
        if lw != p_lw and (not down or lower):
            lw = p_lw if p_lw < hg else 0
        
        if hg != p_hg and (down or higher):
            hg = p_hg if p_hg < lw else 0
        
        if down == down[1]:
            pass
        if down != down[1]:
            if down:
                last_h = hg
                hg_vals.append((i - last_h, high[i]))
            else:
                last_l = lw
                lw_vals.append((i - last_l, low[i]))
    
    zigzag_points = pd.DataFrame({'High_Zigzag': np.array(hg_vals)[:, 1], 'Low_Zigzag': np.array(lw_vals)[:, 1]}, index=np.array(hg_vals)[:, 0])
    return zigzag_points

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username')

args = parser.parse_args()
heroname = args.username

config = get_config_file()
hero = config[heroname]
symbol = 'BTCUSDT_UMCBL'
huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
startTime = get_previous_day_timestamp()
endTime = get_previous_minute_timestamp()
data = huFu.mix_get_candles(symbol, '15m', startTime, endTime)

# 将获取到的数据转换成 DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'Turnover'])
# 调用 ZigZag 函数获取 ZigZag 高低点
zigzag_points = zigzag(df['high'], df['low'])

# 输出 ZigZag 高低点
print(zigzag_points)