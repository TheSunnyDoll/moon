import numpy as np
from math import floor
from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *
# zigzag with fib

## inner circle

## outer ring

## bull leg , 
##      entry at (high - 0.618 * delta) , tp at (high - 0.236 * delta) ,sl at (high - 0.786 * delta)
##      entry at (high - 0.786 * delta) , tp at (high - 0.236 * delta) ,sl at high

## bear leg , 
##      entry at (low + 0.618 * delta)  , tp at (low +0.236 * delta) , sl at (low + 0.786 * delta)
##      entry at (low + 0.786 * delta)  , tp at (low +0.236 * delta) , sl at high



class ZigZag():
    def __init__(self) -> None:
        pass

    def zigzag(self,*, klines, min_size, percent):
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
            big_trend[len(big_trend):] = ['bull', price[low_index], price[high_index]]
            # 将price列表按大小排序，取倒数第二低的值
            price_sorted = sorted(price)
            big_trend.append(price_sorted[1])

            # 0.786
            delta =  price[high_index] - price[low_index]
            idm_1 =  round(price[high_index] - 0.786 * delta + 1)

            # 0.618
            idm_2 =  round(price[high_index] - 0.618 * delta + 1)

            # 0.382
            tp1 =  round(price[high_index] - 0.382 * delta - 1)

            # 0.236
            tp2 =  round(price[high_index] - 0.236 * delta - 1)
            big_trend[len(big_trend):]=[idm_1,idm_2,tp1,tp2]

        else:
            big_trend[len(big_trend):] = ['bear', price[high_index], price[low_index]]
            # 将price列表按大小排序，取第二高的值
            price_sorted = sorted(price, reverse=True)
            big_trend.append(price_sorted[1])

            # 0.786
            delta =  price[high_index] - price[low_index]
            idm_1 =  round(price[low_index] + 0.786 * delta - 1)

            # 0.618
            idm_2 =  round(price[low_index] + 0.618 * delta - 1)

            # 0.382
            tp1 =  round(price[low_index] + 0.382 * delta + 1)

            # 0.236
            tp2 =  round(price[low_index] + 0.236 * delta + 1)
            big_trend[len(big_trend):]=[idm_1,idm_2,tp1,tp2]
        return result,big_trend

    def advortise(self,trend):
        orders = []
        for td in trend:
            ft = td[0]
            sl1 = td[2]
            sl2 = td[4]
            eng_entry = td[4]
            idm1_entry = td[5]
            idm2_entry = td[6]
            tp1 = td[7]
            tp2 = td[8]
            if td[1] == 'bull':
                drec = 'open_long'
            if td[1] == 'bear':
                drec = 'open_short'

            ft_orders = []
            eng_order = [drec,eng_entry,tp1,sl1,ft+'_eng_order']
            idm1_order1 = [drec,idm1_entry,tp1,sl2,ft+'_idm1_order1']
            idm1_order2 = [drec,idm1_entry,tp2,sl2,ft+'_idm1_order2']
            idm2_order1 = [drec,idm2_entry,tp1,sl2,ft+'_idm2_order1']
            idm2_order2 = [drec,idm2_entry,tp2,sl2,ft+'_idm2_order2']
            ft_orders[len(ft_orders):] = [eng_order,idm1_order1,idm1_order2,idm2_order1,idm2_order2]
            orders.append(ft_orders)

        return orders
        

    def batch_orders(self,oders,huFu,marginCoin,base_qty,debug_mode):
        for ft_orders in oders:
            for order in ft_orders:
                if order[0] == 'open_long':
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                if order[0] == 'open_short':
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]

                logger.info("let us take out! 开单方向: %s ,进场点位: %s, 止盈: %s,止损: %s ,标签: %s,止盈点数: %s,止损点数: %s",order[0],order[1],order[2],order[3],order[4],tp_delta,sl_delta)
                if not debug_mode:
                    if sl_delta>=0:
                        huFu.mix_place_plan_order(symbol, marginCoin, base_qty, order[0], 'limit', order[1], "market_price", executePrice=order[1], clientOrderId=order[4],presetTakeProfitPrice=order[2], presetStopLossPrice=order[3], reduceOnly=False)

    def on_track(self,legs,huFu,marginCoin,base_qty,debug_mode):
        base_point = 150
        last_leg = legs[-1]
        delta = abs(last_leg[1]-last_leg[2])
        if delta >= base_point:
            delta_idm1 = delta * 0.786
            delta_idm2 = delta * 0.618
            delta_tp1_idm = delta * 0.382
            delta_tp2_idm = delta * 0.236
            orders = []
            if last_leg[0] == 'bull':
                derc = 'open_long'
                idm1_entry = round(last_leg[2] - delta_idm1 + 1)
                idm2_entry = round(last_leg[2] - delta_idm2 + 1)
                tp1_idm = round(last_leg[2] - delta_tp1_idm - 1)
                tp2_idm = round(last_leg[2] - delta_tp2_idm - 1)

                sl1_idm = last_leg[1]
                sl2_idm = idm1_entry

                idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm]
                idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm]
                idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm]
                idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm]
                orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]

            if last_leg[0] == 'bear':
                derc = 'open_short'
                idm1_entry = round(last_leg[2] + delta_idm1 - 1)
                idm2_entry = round(last_leg[2] + delta_idm2 - 1)
                tp1_idm = round(last_leg[2] + delta_tp1_idm + 1)
                tp2_idm = round(last_leg[2] + delta_tp2_idm + 1)

                sl1_idm = last_leg[1]
                sl2_idm = idm1_entry

                idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm]
                idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm]
                idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm]
                idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm]
                orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]

            for order in orders:
                if order[0] == 'open_long':
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                if order[0] == 'open_short':
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]

                logger.warning("short term meat! 开单方向: %s ,进场点位: %s, 止盈: %s,止损: %s ,止盈点数: %s,止损点数: %s ",order[0],order[1],order[2],order[3],tp_delta,sl_delta)
                if not debug_mode:
                    if sl_delta>=0:
                        huFu.mix_place_plan_order(symbol, marginCoin, base_qty, order[0], 'limit', order[1], "market_price", executePrice=order[1],presetTakeProfitPrice=order[2], presetStopLossPrice=order[3], reduceOnly=False)




def run(hero,symbol,marginCoin,debug_mode):
    base_qty = 0.001
    zz = ZigZag()

    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    while True:
        if not debug_mode:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
            if data != []:
                    ## clear all open orders
                huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

        startTime = get_previous_month_timestamp()
        endTime = get_previous_minute_timestamp()
        if not debug_mode:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
            if data != []:
                    ## clear all open orders
                huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
        trend = []
        ft_list = ['15m','30m','1H','4H','1D']
        last_trend = []
        for ft in ft_list:
            try:
                klines = huFu.mix_get_candles(symbol, ft, startTime, endTime)
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_candles(): {e}")

            r,b = zz.zigzag(klines=klines, min_size=0.0055, percent=True)
            if ft == '15m':
                last_trend = r
            b.insert(0,ft)
            trend.append(b)
            time.sleep(0.3)

        orders = zz.advortise(trend)
        zz.batch_orders(orders,huFu,marginCoin,base_qty,debug_mode)
        for i in range(30):
            zz.on_track(last_trend,huFu,marginCoin,base_qty,debug_mode)

            time.sleep(30)
            if not debug_mode:
                data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
                if data != []:
                    for order in data:
                        if '_' not in order['clientOid']:
                        ## clear all open orders
                            huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'], 'normal_plan')



if __name__ == "__main__":
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')

    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode

    config = get_config_file()
    hero = config[heroname]
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    run(hero,symbol,marginCoin,debug_mode)