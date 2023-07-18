# 1.标记swing_h,swing_l
# 2.如果当前价格低于swing_l,标记当前价格为swing_l,标记当前市场为bear_bias,delta = (swing_h - swing_l)/2 , 标记交易区间DR = （swing_l + delta,swing_h）
# 3.当市场为bear_bias 时,在价格pullback 到DR 且 DR > 30 时,开始观察，如果下一根k线高于当前区间最高价的一根k线，则挂单在最高价k线的（开盘价-5）的位置，止盈放在swing_l，止损放在swing_h，在这根k线收盘时还未进场，则取消订单，等待下一次

import pandas as pd
import numpy as np
from utils import *
from pybitget import Client
import argparse
pd.options.mode.chained_assignment = None  # default='warn'


class PingPong():
    def __init__(self) -> None:
        self.pivots = []

    def find_pivots(self,symbol,huFu):
        startTime = get_previous_three_hour_timestamp()
        endTime = get_previous_minute_timestamp()
        data = huFu.mix_get_candles(symbol, '15m', startTime, endTime)
        # Convert the provided data to a DataFrame
        market_struct = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
        market_struct['Timestamp'] = pd.to_datetime(market_struct['Timestamp'], unit='ms')
        market_struct['bias'] = None
        market_struct['last_king'] = None
        pivots = []
        delta_base = 30
        current_pivot_h = np.nan
        current_pivot_l = np.nan
        for i in range(1, len(market_struct)):
            if len(pivots) == 0:
                if market_struct['Low'][i] < market_struct['Low'][i - 1]:
                    current_pivot_l = market_struct['Low'][i]
                    current_pivot_h = market_struct['High'][i]
                    market_struct['bias'][i] = 'bear'

                    for j in range(i+1,len(market_struct)):
                        if market_struct['Low'][j] < market_struct['Low'][j - 1]:
                            if float(current_pivot_h) - float(current_pivot_l) >= delta_base:
                                pivots.append(['bear', current_pivot_h, current_pivot_l])
                                print(market_struct['Timestamp'][j])
                                print('new')
                                i = j
                                break
                        if market_struct['High'][j] > market_struct['High'][j - 1]:
                            current_pivot_h = market_struct['High'][j]
                            market_struct['last_king'][j] = 'highest'

                            ###
                elif market_struct['High'][i] > market_struct['High'][i - 1]:
                    current_pivot_l = market_struct['Low'][i]
                    current_pivot_h = market_struct['High'][i]
                    market_struct['bias'][i] = 'bull'

                    for j in range(i+1,len(market_struct)):
                        if market_struct['High'][j] > market_struct['High'][j - 1]:
                            if float(current_pivot_h) - float(current_pivot_l) >= delta_base:
                                pivots.append(['bull', current_pivot_h, current_pivot_l])
                                print(market_struct['Timestamp'][j])
                                print('new')
                                i = j
                                break
                        if market_struct['Low'][j] < market_struct['Low'][j - 1]:
                            current_pivot_l = market_struct['Low'][j]
                            market_struct['last_king'][j] = 'lowest'

            else:
                if market_struct['Low'][i] < pivots[-1][2]:
                    current_pivot_l = market_struct['Low'][i]
                    current_pivot_h = market_struct['High'][i]
                    market_struct['bias'][i] = 'bear'
                    for j in range(i+1,len(market_struct)):
                        if market_struct['Low'][j] < market_struct['Low'][j - 1]:
                            if float(current_pivot_h) - float(current_pivot_l) >= delta_base:
                                pivots.append(['bear', current_pivot_h, current_pivot_l])

                                print(market_struct['Timestamp'][j])
                                print('new')
                                i = j
                                break
                        if market_struct['High'][j] > market_struct['High'][j - 1]:
                            current_pivot_h = market_struct['High'][j]
                            market_struct['last_king'][j] = 'highest'
                        if market_struct['High'][j] > pivots[-1][1]:
                            # break block , choch
                            market_struct['bias'][i] = 'demand'
                            i = j
                            break


                elif market_struct['High'][i] > pivots[-1][1]:
                    current_pivot_l = market_struct['Low'][i]
                    current_pivot_h = market_struct['High'][i]
                    market_struct['bias'][i] = 'bull'

                    for j in range(i+1,len(market_struct)):
                        if market_struct['High'][j] > market_struct['High'][j - 1]:
                            if float(current_pivot_h) - float(current_pivot_l) >= delta_base:
                                pivots.append(['bull', current_pivot_h, current_pivot_l])
                                print(market_struct['Timestamp'][j])
                                print('new')
                                i = j
                                break
                        if market_struct['Low'][j] < market_struct['Low'][j - 1]:
                            # break block ,choch
                            current_pivot_l = market_struct['Low'][j]
                            market_struct['last_king'][j] = 'lowest'
                        if market_struct['Low'][j] < pivots[-1][2]:
                            # break block , choch
                            market_struct['bias'][i] = 'supply'
                            i = j
                            break

        last_bias = None
        last_strct = None
        last_entry_base = 0

        bear_index = 0
        bull_index = 0

        bears_pa = market_struct.loc[market_struct['bias']=='bear']
        bulls_pa = market_struct.loc[market_struct['bias']=='bull']
        bulls_lowest = market_struct.loc[market_struct['last_king']=='lowest']
        bears_highest = market_struct.loc[market_struct['last_king']=='highest']


        if not bears_pa.empty:
            bear_base = bears_pa.iloc[-1]
            bear_index = bear_base.name
        if not bulls_pa.empty:
            bull_base = bulls_pa.iloc[-1]
            bull_index = bull_base.name
        if not bears_highest.empty:
            bears_highest_val = bears_highest.iloc[-1]
        if not bulls_lowest.empty:
            bulls_lowest_val = bulls_lowest.iloc[-1]


        if bear_index != 0:
            if bull_index !=0:
                if bear_index > bull_index:
                    last_bias = 'bear'
                    last_strct = bear_base
                    last_entry_base = bears_highest_val
                else:
                    last_bias = 'bull'
                    last_strct = bull_base
                    last_entry_base = bulls_lowest_val
            else:
                last_bias = 'bear'
                last_strct = bear_base
                last_entry_base = bears_highest_val

        elif bull_index !=0:
            last_bias = 'bull'
            last_strct = bull_base
            last_entry_base = bulls_lowest_val

        self.pivots = pivots
        print(market_struct)
        return pivots,last_bias,last_strct,last_entry_base

    def on_minute(self,symbol,huFu,pivots,last_bias,last_strct,last_entry_base):
        if last_bias == 'bear':
            low = min(float(pivots[-1][2]),float(last_strct['Low']))
            high = float(pivots[-2][1])
            delta = round((high - low)/2)
            interview = low + delta
            last_high = float(last_entry_base['High'])
            last_entry = (max(float(last_entry_base['Open']),float(last_entry_base['Close'])) - 5)
            if delta > 20:
            # get current price
            # if cp > interview  && cp > last_high :
            #    tp = low ,sl = high
            #    place order
        ## get current price 
                try:
                    result = huFu.mix_get_market_price(symbol)
                    current_price = result['data']['markPrice']
                    logger.info("斥候来报，坐标 %s 处发现敌军",current_price)
                except Exception as e:
                    logger.warning(f"An unknown error occurred in mix_get_market_price(): {e}")
                if current_price > interview and current_price > last_high:
                    logger.info("最新观测突破点%f\n,最新入场点%f\n,止盈价格%f\n,止损价格%f\n",last_high,last_entry,low,high)

                


            

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    args = parser.parse_args()
    heroname = args.username

    config = get_config_file()
    hero = config[heroname]
    symbol = 'BTCUSDT_UMCBL'
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])

    player = PingPong()

    while True:
        pivots,last_bias,last_strct,last_entry_base = player.find_pivots(symbol,huFu)
        for i in range(3):
            player.on_minute(symbol,huFu,pivots,last_bias,last_strct,last_entry_base)
            time.sleep(300)

if __name__ == "__main__":
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    run()
