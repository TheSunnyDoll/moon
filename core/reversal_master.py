
from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *


class Reversal():
    def __init__(self) -> None:
        pass
    def get_last_bar(self,symbol,huFu,ft):
        if ft == '1m':
            x = 2
        if ft == '5m':
            x= 6
        startTime = get_previous_xmin_timestamp(x)
        endTime = get_previous_xmin_timestamp(1)

        # endTime = get_current_timestamp()

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
        return klines[-1]

def start(hero,symbol,marginCoin,debug_mode):
    rvs = Reversal()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    # last_1m = rvs.get_last_bar(symbol,huFu,'1m')
    last_5m = rvs.get_last_bar(symbol,huFu,'5m')
    print(last_5m)
    # print(last_1m)






if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')

    parser.add_argument('-fp', '--fix_tp_point', default=88,help='fix_tp_point')
    parser.add_argument('-bsl', '--base_sl', default=88,help='base_sl')
    parser.add_argument('-bq', '--base_qty', default=0.05,help='base_qty')
    parser.add_argument('-mxq', '--max_qty', default=1.5,help='max_qty')

    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode
    fix_mode = args.fix_tp_mode
    super_mode = args.super_mode
    fix_tp = float(args.fix_tp_point)
    base_qty = float(args.base_qty)
    base_sl = float(args.base_sl)
    max_qty = float(args.max_qty)

    logger = get_logger(heroname+'_record.log')

    config = get_config_file()
    hero = config[heroname]
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    start(hero,symbol,marginCoin,debug_mode)