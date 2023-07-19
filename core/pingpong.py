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
        self.pivot_highs_long = []
        self.pivot_lows_long = []
        self.pivot_highs_short = []
        self.pivot_lows_short = []
        self.pivot_inter_highs_long = []
        self.pivot_inter_lows_long = []
        self.pivot_inter_highs_short = []
        self.pivot_inter_lows_short = []

        self.old_bias = ''
        self.current_bias = ''
        self.idm = 0
        self.reversal = 0
        self.last_candle_type = ''
        self.observe_candle_type = ''
        self.observe_price = 0

    def find_pivots(self,symbol,huFu):
        startTime = get_previous_day_timestamp()
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

    def find_pivots_lr(self,symbol,huFu,left_len,right_len):
        startTime = get_previous_day_timestamp()
        endTime = get_previous_minute_timestamp()
        data = huFu.mix_get_candles(symbol, '15m', startTime, endTime)
        # Convert the provided data to a DataFrame
        market_struct = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
        market_struct['Timestamp'] = market_struct['Timestamp'].astype(int)
        market_struct['Timestamp'] = pd.to_datetime(market_struct['Timestamp'], unit='ms')
        market_struct['type'] = None

        for i in range(1, len(market_struct)):
            if market_struct['Close'][i] >= market_struct['Open'][i]:
                market_struct['type'][i] = 'bull'
            else:
                market_struct['type'][i] = 'bear'
        self.last_candle_type = market_struct.iloc[-1]['type']
        self.observe_candle_type = market_struct.iloc[-2]['type']
        self.observe_price = round((float(market_struct.iloc[-2]['Open']) + float(market_struct.iloc[-2]['Close']))/2)

        bear_bars = market_struct[market_struct["type"] == 'bear'].reset_index(drop=True)
        bull_bars = market_struct[market_struct["type"] == 'bull'].reset_index(drop=True)
        pivot_highs = []
        pivot_lows = []
        pivot_inter_highs = []
        pivot_inter_lows = []

        for i in range(left_len, len(market_struct) - right_len):

            if market_struct["High"][i] > max(max(market_struct["High"][i-left_len:i]),max(market_struct["High"][i+1:i+right_len+1])):
                pivot_highs.append(float(market_struct["High"][i]))

            if market_struct["Low"][i] < min(min(market_struct["Low"][i-left_len:i]),min(market_struct["Low"][i+1:i+right_len+1])):
                pivot_lows.append(float(market_struct["Low"][i]))

        for i in range(left_len, len(bull_bars) - right_len):
            if bull_bars["Close"][i] > max(max(bull_bars["Close"][i-left_len:i]),max(bull_bars["Close"][i+1:i+right_len+1])):
                pivot_inter_highs.append(float(bull_bars["Close"][i]))

        for i in range(left_len, len(bear_bars) - right_len):
            if bear_bars["Close"][i] < min(min(bear_bars["Close"][i-left_len:i]),min(bear_bars["Close"][i+1:i+right_len+1])):
                pivot_inter_lows.append(float(bear_bars["Close"][i]))


        if left_len >=10:
            self.pivot_highs_long = pivot_highs
            self.pivot_lows_long = pivot_lows
            self.pivot_inter_highs_long = pivot_inter_highs
            self.pivot_inter_lows_long = pivot_inter_lows

        else:
            self.pivot_highs_short = pivot_highs
            self.pivot_lows_short = pivot_lows
            self.pivot_inter_highs_short = pivot_inter_highs
            self.pivot_inter_lows_short = pivot_inter_lows

    def on_minute_move(self,symbol,huFu):
        last_short_high = self.pivot_highs_short[-1]
        last_short_low = self.pivot_lows_short[-1]
        delta = round((last_short_high - last_short_low)/2)
        if delta > 20:
            try:
                result = huFu.mix_get_market_price(symbol)
                current_price = result['data']['markPrice']
                logger.info("斥候来报，坐标 %s 处发现敌军",current_price)
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_market_price(): {e}")

            # if current_price > interview and current_price > last_high:
            #     logger.info("最新观测突破点%f\n,最新入场点%f\n,止盈价格%f\n,止损价格%f\n",last_high,last_entry,low,high)

            if self.current_bias == 'bull':
                # get last 15m candle
                # get current price
                # wait flip 
                pass
            elif self.current_bias == 'bear':
                pass
            elif self.current_bias == 'weak_bull':
                pass
            elif self.current_bias == 'weak_bear':
                pass



    def get_current_bias(self):
        last_long_high = self.pivot_highs_long[-1]
        last_long_low = self.pivot_lows_long[-1]
        last_short_high = self.pivot_highs_short[-1]
        last_short_low = self.pivot_lows_short[-1]

        self.old_bias = self.current_bias

        if last_short_high > last_long_high:
            self.current_bias = 'bull'
        elif last_short_low < last_long_low:
            self.current_bias = 'bear'
        elif last_short_high > self.pivot_highs_short[-2]:
            self.current_bias = 'weak_bull'
        elif last_short_low < self.pivot_lows_short[-2]:
            self.current_bias = 'weak_bear'

    def mark_some_points(self):
        if self.current_bias == 'weak_bear' or self.current_bias == 'bull':
            self.idm = min(self.pivot_lows_short[-3:])
            self.reversal = max(self.pivot_inter_highs_short)

        elif self.current_bias == 'weak_bull' or self.current_bias == 'bear' :
            self.idm = max(self.pivot_highs_short[-3:])
            self.reversal = min(self.pivot_inter_lows_short)

    def advertise(self):
        if (self.old_bias == 'bull' and self.current_bias == 'weak_bear') or (self.old_bias == 'bear' and self.current_bias == 'weak_bull'):
            entry = self.idm
            tp = self.reversal
            sl = self.idm - 60
            delta = tp - entry
            if delta >= 60:
                logger.info("推荐进场点位 :%s,止盈点位%s,止损点位%s",entry,tp,sl)


    def track(self,huFu,symbol):
        startTime = get_previous_hour_timestamp()
        endTime = get_previous_minute_timestamp()
        data = huFu.mix_get_candles(symbol, '15m', startTime, endTime)
        # Convert the provided data to a DataFrame
        market_struct = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
        market_struct['Timestamp'] = market_struct['Timestamp'].astype(int)
        market_struct['Timestamp'] = pd.to_datetime(market_struct['Timestamp'], unit='ms')
        market_struct['type'] = None

        for i in range(1, len(market_struct)):
            if market_struct['Close'][i] >= market_struct['Open'][i]:
                market_struct['type'][i] = 'bull'
            else:
                market_struct['type'][i] = 'bear'
        self.last_candle_type = market_struct.iloc[-1]['type']
        self.observe_candle_type = market_struct.iloc[-2]['type']
        self.observe_price = round((float(market_struct.iloc[-2]['Open']) + float(market_struct.iloc[-2]['Close']))/2)



        if not ((self.old_bias == 'bull' and self.current_bias == 'weak_bear') or (self.old_bias == 'bear' and self.current_bias == 'weak_bull')):
            if self.current_bias == 'weak_bear' or self.current_bias == 'bear':
                if self.observe_candle_type == 'bear':
                    logger.info("时机未到,坐等一根🐮🐮🌈出现")
                elif self.observe_candle_type == 'bull':
                    if self.last_candle_type == 'bear':
                        sl = self.pivot_highs_short[-1]
                        tp = self.pivot_lows_short[-1]
                        tp_delta = float(self.observe_price - float(tp))
                        sl_delta = float(float(sl) - self.observe_price)

                        logger.info("🐮🐮💤,🐻🐻开始🏃吧,观察空单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                        if tp_delta >= sl_delta:
                            logger.info("🐮🐮💤,🐻🐻开始🏃吧,设置空单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                            if sl_delta <= 100:
                                logger.info("🐮🐮💤,🐻🐻开始🏃吧,加倍设置空单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                    elif self.last_candle_type == 'bull':
                        logger.info("🐻🐻持续向上回头中,现在至少有两根🐮🐮")
                    # flip modle
            if self.current_bias == 'weak_bull' or self.current_bias == 'bull':
                if self.observe_candle_type == 'bull':
                    logger.info("时机未到,坐等一根🐻🐻🌈出现")
                elif self.observe_candle_type == 'bear':
                    if self.last_candle_type == 'bull':
                        tp = self.pivot_highs_short[-1]
                        sl = self.pivot_lows_short[-1]
                        tp_delta = float(float(tp) - self.observe_price)
                        sl_delta = float(self.observe_price - float(sl))

                        logger.info("🐻🐻💤,🐮🐮开始🏃吧,观察多单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                        if tp_delta >= sl_delta:
                            logger.info("🐻🐻💤,🐮🐮开始🏃吧,设置多单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                            if sl_delta <= 100:
                                logger.info("🐻🐻💤,🐮🐮开始🏃吧,加倍设置多单点位 %s ,止盈点位 %s,止损点位 %s ,止盈段 %d , 止损段 %d,",self.observe_price,tp,sl,tp_delta,sl_delta)
                    elif self.last_candle_type == 'bear':
                        logger.info("🐮🐮持续向下回头中,现在至少有两根🐻🐻")


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
        player.find_pivots_lr(symbol,huFu,10,10)
        player.find_pivots_lr(symbol,huFu,2,2)
        player.get_current_bias()
        player.mark_some_points()
        player.advertise()
        logger.info("现在趋势:%s to %s , 陷阱位 : %s , 潜在反转位: %s ,最后一根蜡烛是 %s",player.old_bias,player.current_bias,player.idm,player.reversal,player.last_candle_type)

        for i in range(30):
            player.track(huFu,symbol)
            time.sleep(30)
        # cancel all plan order

if __name__ == "__main__":
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    run()
