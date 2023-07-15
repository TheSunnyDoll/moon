from utils import *
from pybitget import Client
import argparse

# special time 
##  bj  22:00 - 23:00         14:00 - 15:00
##  utc 14:00 - 15:00         07:00 - 08:00
## lft - 5m -3m


## 寻找21:00 后的fvg，在21:50分，将单子挂向前一个 3m fvg 


## setup：
## UTC 13:45 , 获取前60根 3m数据，找出其中所有fvg
## 标记fvg

class SilverBullet():
    def __init__(self) -> None:
        pass

    def get_fvg(self,huFu,symbol):

        startTime = get_previous_three_hour_timestamp()
        endTime = get_previous_minute_timestamp()
        ## OHLC 2,3
        data = huFu.mix_get_candles(symbol,'3m',startTime,endTime)
        print(len(data))
        # 2. 寻找FVG并打印
        for item in data:
            print(item)
            open_price = float(item[1])
            high_price = float(item[2])
            low_price = float(item[3])
            close_price = float(item[4])
            
            # 计算FVG条件
            if open_price < low_price and close_price > high_price:
                print("FVG 发现！时间:", item[0], "，开盘价:", open_price, "，最高价:", high_price, "，最低价:", low_price, "，收盘价:", close_price)

    def is_sb_session():
        pass



def run(hero,symbol):

    huFu = Client(hero['api_key'],hero['secret_key'],hero['passphrase'])
    sb = SilverBullet()
    sb.get_fvg(huFu,symbol)

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
