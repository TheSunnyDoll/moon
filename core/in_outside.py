##


from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *


class SideBar():
    def __init__(self) -> None:
        pass
    def get_last_bar(self,symbol,huFu,ft):
        if ft == '1m':
            x = 2
        if ft == '5m':
            x= 16
        startTime = get_previous_xmin_timestamp(x)
        endTime = get_minute_timestamp()

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
        return klines[-3:]

    def inside_outside(self,bars):
        def is_inside_bar(pre,current):
            if current[2] <= pre[2] and current[3]>= pre[3]:
                return True
            else:
                return False
        
        def is_outside_bar(pre,current):
            if current[2] >= pre[2] and current[3] <= pre[3]:
                return True
            else:
                return False
        
        if is_inside_bar(bars[0],bars[1]):
            if is_outside_bar(bars[1],bars[2]):
                return 'short'
        elif is_outside_bar(bars[0],bars[1]):
            if is_inside_bar(bars[1],bars[2]):
                return 'long'  
        else:
            return ''

        # if bar[1] inside bar ; bar[2] outside ; sell
        # if bar[2] inside bar ; bar[1] outside ; buy

    def place_order(self,side,huFu,symbol,marginCoin):
        base_qty = 0.01
        if side == 'long':
            # get position; close short ; entry long
            try:
                result = huFu.mix_get_single_position(symbol,marginCoin)
                pos = result['data']

            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_get_single_position(): {e}")
            
            long_qty = float(pos[0]["total"])
            short_qty = float(pos[1]["total"])

            if short_qty >0:
                try:

                    huFu.mix_place_order(symbol,'USDT',short_qty,'close_short','market',reduceOnly=True)
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_place_order(): {e}")
            try:
                if long_qty == 0:
                    huFu.mix_place_order(symbol,'USDT',base_qty,'open_long','market',reduceOnly=False)
                    logger.info("open long")

            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_place_order(): {e}")

        elif side == 'short':
            # get position; close short ; entry long
            try:
                result = huFu.mix_get_single_position(symbol,marginCoin)
                pos = result['data']

            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_get_single_position(): {e}")
            
            long_qty = float(pos[0]["total"])
            short_qty = float(pos[1]["total"])

            if long_qty >0:
                try:

                    huFu.mix_place_order(symbol,'USDT',long_qty,'close_long','market',reduceOnly=True)
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_place_order(): {e}")
            try:
                if short_qty == 0:
                    huFu.mix_place_order(symbol,'USDT',base_qty,'open_short','market',reduceOnly=False)
                    logger.info("open short")
            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_place_order(): {e}")
            

def start(hero,symbol,marginCoin,debug_mode):
    rvs = SideBar()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    # last_1m = rvs.get_last_bar(symbol,huFu,'1m')
    while True:
        last_5m_bars = rvs.get_last_bar(symbol,huFu,'5m')

        # print(last_1m)
        side = rvs.inside_outside(last_5m_bars)
        if side != '':
            rvs.place_order(side,huFu,symbol,marginCoin)

        time.sleep(10)


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