


## triangle
## inside bar
from utils import *
import argparse

def get_klines(huFu):
    startTime = get_previous_month_timestamp()
    endTime = get_previous_minute_timestamp()
    trend = []
    # ft_list = ['5m','15m','30m','1H','4H','1D']
    ft_list = ['5m']
    last_legs = []
    last_klines = []
    for ft in ft_list:

        max_retries = 3
        retry_delay = 1  # 延迟时间，单位为秒
        retry_count = 0
        klines = []

        while not klines and retry_count < max_retries:
            try:
                klines = huFu.mix_get_candles(symbol, ft, startTime, endTime)
            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_get_candles(): {e} ,{ft}")
            
            if not klines:
                retry_count += 1
                print("再来一次")
                time.sleep(retry_delay)
        # if ft != '5m':
        #     r,b = bb.zigzag(klines=klines, min_size=0.0055, percent=True)           # 0.0055

        #     if ft == '1H':
        #         one_H_legs = r
        #     b.insert(0,ft)
        #     trend.append(b)
        # if ft == '5m':
        #     r,b = bb.zigzag(klines=klines, min_size=0.0015, percent=True)           # 0.0015

        #     last_klines = klines
        #     five_legs = r
        time.sleep(0.3)
    return klines

def get_inside_bars(klines):
    def is_inside_bar(current_high, current_low, prev_high, prev_low):
        # 判断当前蜡烛是否是Inside Bar
        if current_high <= prev_high and current_low >= prev_low:
            return True
        else:
            return False

    inside_bars = []

    for i in range(1, len(klines)):
        current_kline = klines[i]
        prev_kline = klines[i - 1]

        current_high = current_kline['high']
        current_low = current_kline['low']
        prev_high = prev_kline['high']
        prev_low = prev_kline['low']

        if is_inside_bar(current_high, current_low, prev_high, prev_low):
            inside_bars.append(current_kline)

    return inside_bars

def run(hero,symbol):
    get_klines()


if __name__ == '__main__':
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    args = parser.parse_args()
    heroname = args.username
    config = get_config_file()
    hero = config[heroname]
    run(hero,symbol)
