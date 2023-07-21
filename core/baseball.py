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

## 动态止损
## 15m 级别 , 盈利 88 开始挪动, 可接受回撤 44 点
## 30m 级别 , 盈利 166 开始挪动, 可接受回撤 88 点
## 1h 级别 , 盈利 199 开始挪动, 可接受回撤 88 点
## 4h 级别 , 盈利 299 开始挪动, 可接受回撤 88 点
## 1d 级别 , 盈利 399 开始挪动, 可接受回撤 88 点



class BaseBall():
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

    def advortise(self,trend,fix_mode,fix_tp):
        orders = []
        for td in trend:
            ft = td[0]
            sl1 = td[2]
            eng_entry = td[4]
            idm1_entry = td[5]
            idm2_entry = td[6]
            tp1 = td[7]
            tp2 = td[8]

            if td[1] == 'bull':
                drec = 'open_long'
                sl2 = td[4] - 20
                eng_tp3 = eng_entry + fix_tp
                idm1_tp3 = idm1_entry + fix_tp
                idm2_tp3 = idm2_entry + fix_tp

            if td[1] == 'bear':
                drec = 'open_short'
                sl2 = td[4] + 20
                eng_tp3 = eng_entry - fix_tp
                idm1_tp3 = idm1_entry - fix_tp
                idm2_tp3 = idm2_entry - fix_tp


            ft_orders = []
            if not fix_mode:
                eng_order = [drec,eng_entry,tp1,sl1,ft+'_eng_order']
                idm1_order1 = [drec,idm1_entry,tp1,sl2,ft+'_idm1_order1']
                idm1_order2 = [drec,idm1_entry,tp2,sl2,ft+'_idm1_order2']
                idm2_order1 = [drec,idm2_entry,tp1,sl2,ft+'_idm2_order1']
                idm2_order2 = [drec,idm2_entry,tp2,sl2,ft+'_idm2_order2']
                ft_orders[len(ft_orders):] = [eng_order,idm1_order1,idm1_order2,idm2_order1,idm2_order2]
            else:
                eng_order_fix_tp = [drec,eng_entry,eng_tp3,sl1,ft+'_eng_order_fix_tp']
                idm1_order1_fix_tp = [drec,idm1_entry,idm1_tp3,sl2,ft+'_idm1_order1_fix_tp']
                idm1_order2_fix_tp = [drec,idm1_entry,idm1_tp3,sl2,ft+'_idm1_order2_fix_tp']
                idm2_order1_fix_tp = [drec,idm2_entry,idm2_tp3,sl2,ft+'_idm2_order1_fix_tp']
                idm2_order2_fix_tp = [drec,idm2_entry,idm2_tp3,sl2,ft+'_idm2_order2_fix_tp']
                ft_orders[len(ft_orders):] = [eng_order_fix_tp,idm1_order1_fix_tp,idm1_order2_fix_tp,idm2_order1_fix_tp,idm2_order2_fix_tp]

            orders.append(ft_orders)

        return orders
        

    def batch_orders(self,oders,huFu,marginCoin,base_qty,debug_mode,base_sl,current_price):
        for ft_orders in oders:
            for order in ft_orders:
                time.sleep(0.3)
                hft_qty = base_qty
                if order[0] == 'open_long':
                    if current_price < order[1]:
                        continue
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] - base_sl
                        sl_delta = base_sl
                    else:
                        sl = order[3]
                if order[0] == 'open_short':
                    if current_price > order[1]:
                        continue
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] + base_sl
                        sl_delta = base_sl
                    else:
                        sl = order[3]
                
                logger.info("来吧全垒打⚾️ !我准备好啦! 🥖击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta)
                if not debug_mode:
                    if sl_delta>=0:
                        if order[1] > 30900:
                            hft_qty = 0.6
                        try:
                            huFu.mix_place_plan_order(symbol, marginCoin, hft_qty, order[0], 'limit', order[1], "market_price", executePrice=order[1], clientOrderId=order[4],presetTakeProfitPrice=order[2], presetStopLossPrice=sl, reduceOnly=False)
                        except Exception as e:
                            logger.warning(f"An unknown error occurred in mix_place_plan_order(): {e}")


    def on_track(self,legs,huFu,marginCoin,base_qty,debug_mode,base_sl,fix_mode,fix_tp):
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
                sl2_idm = idm1_entry - 20

                if not fix_mode:

                    idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm,'firsebase-idm1-1']
                    idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm,'firsebase-idm1_2']
                    idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm,'firsebase-idm2-1']
                    idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm,'firsebase-idm2-2']
                    orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]

                else:
                    idm1_tp = idm1_entry + fix_tp
                    idm2_tp = idm2_entry + fix_tp

                    idm1_order1_fix_tp = [derc,idm1_entry,idm1_tp,sl1_idm,'firsebase-idm1-1-fxtp']
                    idm1_order2_fix_tp = [derc,idm1_entry,idm1_tp,sl1_idm,'firsebase-idm1-2-fxtp']
                    idm2_order1_fix_tp = [derc,idm2_entry,idm2_tp,sl2_idm,'firsebase-idm2-1-fxtp']
                    idm2_order2_fix_tp = [derc,idm2_entry,idm2_tp,sl2_idm,'firsebase-idm2-2-fxtp']
                    orders[len(orders):] = [idm1_order1_fix_tp,idm1_order2_fix_tp,idm2_order1_fix_tp,idm2_order2_fix_tp]

            if last_leg[0] == 'bear':
                derc = 'open_short'
                idm1_entry = round(last_leg[2] + delta_idm1 - 1)
                idm2_entry = round(last_leg[2] + delta_idm2 - 1)
                tp1_idm = round(last_leg[2] + delta_tp1_idm + 1)
                tp2_idm = round(last_leg[2] + delta_tp2_idm + 1)

                sl1_idm = last_leg[1]
                sl2_idm = idm1_entry + 20

                if not fix_mode:
                    idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm,'firsebase-idm1-1']
                    idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm,'firsebase-idm1_2']
                    idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm,'firsebase-idm2-1']
                    idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm,'firsebase-idm2-2']
                    orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]
                
                else:
                    idm1_tp = idm1_entry - fix_tp
                    idm2_tp = idm2_entry - fix_tp

                    idm1_order1_fix_tp = [derc,idm1_entry,idm1_tp,sl1_idm,'firsebase-idm1-1-fxtp']
                    idm1_order2_fix_tp = [derc,idm1_entry,idm1_tp,sl1_idm,'firsebase-idm1-2-fxtp']
                    idm2_order1_fix_tp = [derc,idm2_entry,idm2_tp,sl2_idm,'firsebase-idm2-1-fxtp']
                    idm2_order2_fix_tp = [derc,idm2_entry,idm2_tp,sl2_idm,'firsebase-idm2-2-fxtp']
                    orders[len(orders):] = [idm1_order1_fix_tp,idm1_order2_fix_tp,idm2_order1_fix_tp,idm2_order2_fix_tp]

            for order in orders:
                if order[0] == 'open_long':
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] - base_sl
                        sl_delta = base_sl
                    else:
                        sl = order[3]
                if order[0] == 'open_short':
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] + base_sl
                        sl_delta = base_sl
                    else:
                        sl = order[3]
                logger.warning("一垒就交给我了!⛳️  击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta)   

                if not debug_mode:
                    if sl_delta>=0:
                        try:
                            huFu.mix_place_plan_order(symbol, marginCoin, base_qty, order[0], 'limit', order[1], "market_price", executePrice=order[1], clientOrderId=order[4],presetTakeProfitPrice=order[2], presetStopLossPrice=sl, reduceOnly=False)
                        except Exception as e:
                            logger.warning(f"An unknown error occurred in mix_place_plan_order(): {e}")
        return orders


    def record(self,current_price,pos,orders,track_orders):
        
        long_info  = [float(pos[0]["total"]),float(pos[0]['averageOpenPrice']),pos[0]['achievedProfits'],pos[0]['unrealizedPL']]
        short_info = [float(pos[1]["total"]),float(pos[1]['averageOpenPrice']),pos[1]['achievedProfits'],pos[1]['unrealizedPL']]
        delta = 0
        if short_info[0] > 0:
            delta = short_info[1] - current_price
            logger.critical("short position : %f ,得分圈 :%f",short_info[1],delta)
        if long_info[0] > 0:
            delta = current_price - long_info[0]
            logger.critical("long position : %f ,得分圈 :%f",long_info[1],delta)

        for ft_orders in orders:
            for order in ft_orders:
                entry = order[1]
                label = order[4]
                if short_info[1] == entry or long_info[1] == entry:
                    logger.critical("球员记分,编号: %s, 进场位 %f, 得分圈%f",label,entry,delta)


        for order in track_orders:
                entry = order[1]
                label = order[4]
                if short_info[1] == entry or long_info[1] == entry:
                    logger.critical("球员记分,编号: %s, 进场位 %f, 得分圈%f",label,entry,delta)



def run(hero,symbol,marginCoin,debug_mode,fix_mode,fix_tp,base_qty,base_sl):

    bb = BaseBall()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    if not debug_mode:
        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
                ## clear all open orders
            huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
    logger.warning("三")
    time.sleep(1)
    logger.warning("二")
    time.sleep(1)
    logger.warning("一")
    time.sleep(1)
    logger.warning("比赛开始 🏎️  🏎️ 🏎️ 🏎️🏎️ !!!")

    while True:
        if not debug_mode:
            try:
                data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

            if data != []:
                    ## clear all open orders
                try:
                    huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
                except Exception as e:
                    logger.warning(f"An unknown error occurred in mix_cancel_all_trigger_orders(): {e}")

        startTime = get_previous_month_timestamp()
        endTime = get_previous_minute_timestamp()
        trend = []
        ft_list = ['15m','30m','1H','4H','1D']
        last_trend = []
        for ft in ft_list:
            try:
                klines = huFu.mix_get_candles(symbol, ft, startTime, endTime)
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_candles(): {e}")

            r,b = bb.zigzag(klines=klines, min_size=0.0055, percent=True)
            if ft == '15m':
                last_trend = r
            b.insert(0,ft)
            trend.append(b)
            time.sleep(0.3)
        orders = bb.advortise(trend,fix_mode,fix_tp)
        bb.batch_orders(orders,huFu,marginCoin,base_qty,debug_mode,base_sl,current_price)
        for i in range(30):
            try:
                result = huFu.mix_get_single_position(symbol,marginCoin)
                pos = result['data']
                long_qty = float(pos[0]["total"])
                short_qty = float(pos[1]["total"])
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_single_position(): {e}")
            if long_qty <=0.6 and short_qty<= 0.6:
                track_orders = bb.on_track(last_trend,huFu,marginCoin,base_qty,debug_mode,base_sl,fix_mode,fix_tp)
            try:
                result = huFu.mix_get_market_price(symbol)
                current_price = float(result['data']['markPrice'])
                logger.info("裁判播报员: ⚾️ 坐标 %s ",current_price)
            except Exception as e:
                logger.warning(f"An unknown error occurred in mix_get_market_price(): {e}")

            bb.record(current_price,pos,orders,track_orders)
            time.sleep(30)
            if not debug_mode:
                try:
                    data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
                except Exception as e:
                    logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

                if data != []:
                    for order in data:
                        if '_' not in order['clientOid']:
                        ## clear all open orders
                            try:
                                huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'], 'normal_plan')
                            except Exception as e:
                                logger.warning(f"An unknown error occurred in mix_cancel_plan_order(): {e}")




if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-fp', '--fix_tp_point', default=88,help='fix_tp_point')
    parser.add_argument('-bq', '--base_qty', default=0.05,help='base_qty')
    parser.add_argument('-bsl', '--base_sl', default=88,help='base_sl')

    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode
    fix_mode = args.fix_tp_mode
    fix_tp = float(args.fix_tp_point)
    base_qty = float(args.base_qty)
    base_sl = float(args.base_sl)

    logger = get_logger(heroname+'_record.log')

    config = get_config_file()
    hero = config[heroname]
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    logger.info("让场子热起来吧🔥！ 新一场棒球比赛即将开始⚾️～")
    run(hero,symbol,marginCoin,debug_mode,fix_mode,fix_tp,base_qty,base_sl)