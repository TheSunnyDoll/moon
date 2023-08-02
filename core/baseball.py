from math import floor
from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *
from situation import get_max_pains
from risk_manager import *
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


## TODO:引入order_block , break_block 和 pin_bar


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

        elif low_index > high_index:

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

    def determine_trend(self,zigzag_pattern):
        trend = []
        prev_trend = None

        for i in range(1, len(zigzag_pattern)):
            prev_leg = zigzag_pattern[i - 1]
            current_leg = zigzag_pattern[i]

            if prev_leg[0] == 'bear' and current_leg[0] == 'bull':
                if current_leg[2] > prev_leg[1]:  # Compare bull leg's highest with bear leg's lowest
                    if prev_trend == 'bull' or prev_trend == 'bull_pullback':
                        trend.append('bull')
                    elif prev_trend == 'bear_pullback':
                        trend.append('reversal-bull')
                    else:
                        trend.append('reversal-bull')
                else:
                    trend.append('bear_pullback')
            elif prev_leg[0] == 'bull' and current_leg[0] == 'bear':
                if current_leg[2] < prev_leg[1]:  # Compare bear leg's lowest with bull leg's highest
                    if prev_trend == 'bear' or prev_trend == 'bear_pullback':
                        trend.append('bear')
                    elif prev_trend == 'bull_pullback':
                        trend.append('reversal-bear')
                    else:
                        trend.append('reversal-bear')
                else:
                    trend.append('bull_pullback')

            prev_trend = trend[-1] if trend else None

        return trend


    def advortise(self,trend,fix_mode,fix_tp):
        orders = []
        for td in trend:
            positive = False
            if len(td)<2:
                continue
            ft = td[0]
            sl1 = td[2]
            eng_entry = td[4]
            idm1_entry = td[5]
            idm2_entry = td[6]
            tp1 = td[7]
            tp2 = td[8]

            if td[1] == 'bull':
                drec = 'open_long'
                if tp1 > eng_entry:
                    positive = True
                sl2 = td[4] - 20
                eng_tp3 = eng_entry + fix_tp
                idm1_tp3 = idm1_entry + fix_tp
                idm2_tp3 = idm2_entry + fix_tp

            if td[1] == 'bear':
                drec = 'open_short'
                if tp1 < eng_entry:
                    positive = True
                sl2 = td[4] + 20
                eng_tp3 = eng_entry - fix_tp
                idm1_tp3 = idm1_entry - fix_tp
                idm2_tp3 = idm2_entry - fix_tp


            ft_orders = []
            if not fix_mode:
                if positive:
                    eng_order = [drec,eng_entry,tp1,sl1,ft+'_eng_order']
                idm1_order1 = [drec,idm1_entry,tp1,sl2,ft+'_idm1_order1']
                idm1_order2 = [drec,idm1_entry,tp2,sl2,ft+'_idm1_order2']
                idm2_order1 = [drec,idm2_entry,tp1,sl2,ft+'_idm2_order1']
                idm2_order2 = [drec,idm2_entry,tp2,sl2,ft+'_idm2_order2']
                ft_orders[len(ft_orders):] = [eng_order,idm1_order1,idm1_order2,idm2_order1,idm2_order2]
            else:
                if positive:
                    eng_order_fix_tp = [drec,eng_entry,eng_tp3,sl1,ft+'_eng_order_fix_tp']
                idm1_order1_fix_tp = [drec,idm1_entry,idm1_tp3,sl2,ft+'_idm1_order1_fix_tp']
                idm1_order2_fix_tp = [drec,idm1_entry,idm1_tp3,sl2,ft+'_idm1_order2_fix_tp']
                idm2_order1_fix_tp = [drec,idm2_entry,idm2_tp3,sl2,ft+'_idm2_order1_fix_tp']
                idm2_order2_fix_tp = [drec,idm2_entry,idm2_tp3,sl2,ft+'_idm2_order2_fix_tp']
                ft_orders[len(ft_orders):] = [eng_order_fix_tp,idm1_order1_fix_tp,idm1_order2_fix_tp,idm2_order1_fix_tp,idm2_order2_fix_tp]

            orders.append(ft_orders)

        orders = remove_duplicates(orders)

        return orders
        

    def batch_orders(self,oders,huFu,marginCoin,base_qty,debug_mode,base_sl,current_price,super_mode,dtrend,recent_open_long_list,recent_open_short_list,long_qty,short_qty):
        min_sl = 30
        base_sl_delta = 100

        if super_mode:
            base_sl = 30
            base_sl_delta = 40

        for ft_orders in oders:
            for order in ft_orders:
                time.sleep(0.1)
                if order[0] == 'open_long':
                    if current_price < order[1]:
                        continue
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                    if sl_delta <= 0 or sl_delta >= base_sl_delta:
                        sl = order[1] - base_sl
                        sl_delta = base_sl
                    elif sl_delta < min_sl:
                        sl = order[1] - min_sl
                        sl_delta = min_sl
                    else:
                        sl = order[3]
                if order[0] == 'open_short':
                    if current_price > order[1]:
                        continue
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]
                    if sl_delta <= 0 or sl_delta >= base_sl_delta:
                        sl = order[1] + base_sl
                        sl_delta = base_sl
                    elif sl_delta < min_sl:
                        sl = order[1] + min_sl
                        sl_delta = min_sl
                    else:
                        sl = order[3]

                # hft_qty = round(base_qty * round(tp_delta/sl_delta),2)
                hft_qty = base_qty
                if sl_delta>=0 and tp_delta>=0:
                    if tp_delta < sl_delta:
                        hft_qty = round(base_qty * tp_delta/sl_delta,3)
                if hft_qty > 5:
                    hft_qty = 5
                if dtrend is not None:
                    if dtrend[-1] == 'bear' or dtrend[-1] == 'reversal-bear' or dtrend[-1] == 'bear_pullback':
                        if order[0] != 'open_short':
                            continue
                    elif dtrend[-1] == 'bull' or dtrend[-1] == 'reversal-bull' or dtrend[-1] == 'bull_pullback':
                        if order[0] != 'open_long':
                            continue
                
                if debug_mode:
                    if ((float(order[1]) not in [entry[1] for entry in recent_open_long_list]) or long_qty <= 0) and ((float(order[1]) not in [entry[1] for entry in recent_open_short_list]) or short_qty <= 0):
                        logger.info("来吧全垒打⚾️ !我准备好啦! 🥖击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s,出手数: %s",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta,hft_qty)
                if not debug_mode:
                    if sl_delta>=0 and tp_delta>=0:
                        try:
                            trigger_price = order[1]
                            if order[0] == 'open_long':
                                trigger_price += 1
                            if order[0] == 'open_short':
                                trigger_price -= 1
                            if ((float(order[1]) not in [entry[1] for entry in recent_open_long_list]) or long_qty <= 0) and ((float(order[1]) not in [entry[1] for entry in recent_open_short_list]) or short_qty <= 0):
                                huFu.mix_place_plan_order(symbol, marginCoin, hft_qty, order[0], 'limit', trigger_price, "market_price", executePrice=order[1], clientOrderId=order[4],presetTakeProfitPrice=order[2], presetStopLossPrice=sl, reduceOnly=False)
                                logger.info("来吧全垒打⚾️ !我准备好啦! 🥖击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s,出手数: %s",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta,hft_qty)

                        except Exception as e:
                            logger.debug(f"An unknown error occurred in mix_place_plan_order(): {e}")


    def on_track(self,legs,huFu,marginCoin,base_qty,debug_mode,base_sl,pos,max_qty,dtrend,recent_open_long_list,recent_open_short_list,long_qty,short_qty,batch_orders):
        min_sl = 30
        long_qty = float(pos[0]["total"])
        short_qty = float(pos[1]["total"])
        base_point = 150
        if debug_mode:
            print(legs)
        last_leg = legs[-1]
        delta = abs(last_leg[1]-last_leg[2])
        if delta >= base_point:
            delta_idm1 = delta * 0.786
            delta_idm2 = delta * 0.618
            delta_tp1_idm = delta * 0.382
            delta_tp2_idm = delta * 0.236
            orders = []
            if last_leg[0] == 'bull' or last_leg[0] == 'reversal-bull':
                derc = 'open_long'
                idm1_entry = round(last_leg[2] - delta_idm1 + 1)
                idm2_entry = round(last_leg[2] - delta_idm2 + 1)
                tp1_idm = round(last_leg[2] - delta_tp1_idm - 1)
                tp2_idm = round(last_leg[2] - delta_tp2_idm - 1)

                sl1_idm = last_leg[1]
                sl2_idm = idm1_entry - 20

                idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm,'firsebase-idm1-1']
                idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm,'firsebase-idm1-2']
                idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm,'firsebase-idm2-1']
                idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm,'firsebase-idm2-2']
                orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]


            if last_leg[0] == 'bear' or last_leg[0] == 'reversal-bear':
                derc = 'open_short'
                idm1_entry = round(last_leg[2] + delta_idm1 - 1)
                idm2_entry = round(last_leg[2] + delta_idm2 - 1)
                tp1_idm = round(last_leg[2] + delta_tp1_idm + 1)
                tp2_idm = round(last_leg[2] + delta_tp2_idm + 1)

                sl1_idm = last_leg[1]
                sl2_idm = idm1_entry + 20


                idm1_order1 = [derc,idm1_entry,tp1_idm,sl1_idm,'firsebase-idm1-1']
                idm1_order2 = [derc,idm1_entry,tp2_idm,sl1_idm,'firsebase-idm1-2']
                idm2_order1 = [derc,idm2_entry,tp1_idm,sl2_idm,'firsebase-idm2-1']
                idm2_order2 = [derc,idm2_entry,tp2_idm,sl2_idm,'firsebase-idm2-2']
                orders[len(orders):] = [idm1_order1,idm1_order2,idm2_order1,idm2_order2]
            
            for order in orders:
                if order[0] == 'open_long':
                    tp_delta = order[2] - order[1]
                    sl_delta = order[1] - order[3]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] - base_sl
                        sl_delta = base_sl
                    elif sl_delta < min_sl:
                        sl = order[1] - min_sl
                        sl_delta = min_sl
                    else:
                        sl = order[3]
                if order[0] == 'open_short':
                    tp_delta = order[1] - order[2]
                    sl_delta = order[3] - order[1]
                    if sl_delta <= 0 or sl_delta >= 100:
                        sl = order[1] + base_sl
                        sl_delta = base_sl
                    elif sl_delta < min_sl:
                        sl = order[1] + min_sl
                        sl_delta = min_sl
                    else:
                        sl = order[3]

                if dtrend is not None:
                    if dtrend[-1] == 'bear' or dtrend[-1] == 'reversal-bear' or dtrend[-1] == 'bear_pullback':
                        if order[0] != 'open_short':
                            continue
                    elif dtrend[-1] == 'bull' or dtrend[-1] == 'reversal-bull' or dtrend[-1] == 'bull_pullback':
                        if order[0] != 'open_long':
                            continue
                
                if debug_mode:
                    print(last_leg)
                    cent_qty = base_qty
                    if check_element_in_list(batch_orders,order[1]):
                        cent_qty = round(cent_qty / 2 ,3)
                    if order[1] == idm2_entry:
                        if order[0] == 'open_short':
                            if sl < idm1_entry:
                                cent_qty = round(cent_qty / 4 ,3)
                        if order[0] == 'open_long':
                            if sl > idm1_entry:
                                cent_qty = round(cent_qty / 4 ,3)


                    print("new cent",cent_qty)
                    if ((float(order[1]) not in [entry[1] for entry in recent_open_long_list]) or long_qty <= 0) and ((float(order[1]) not in [entry[1] for entry in recent_open_short_list]) or short_qty <= 0):
                        logger.info("一垒就交给我了!⛳️  击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta)  


                if not debug_mode:
                    if sl_delta>=0 and long_qty <= max_qty and short_qty<= max_qty:
                        try:
                            # cent_qty = round(base_qty * round(tp_delta/sl_delta),2)
                            cent_qty = base_qty
                            if check_element_in_list(batch_orders,order[1]):
                                cent_qty = round(cent_qty / 2 ,3)
                            if cent_qty > 2:
                                cent_qty = 2
                            trigger_price = order[1]
                            if order[0] == 'open_long':
                                trigger_price += 1
                            if order[0] == 'open_short':
                                trigger_price -= 1
                            if ((float(order[1]) not in [entry[1] for entry in recent_open_long_list]) or long_qty <= 0) and ((float(order[1]) not in [entry[1] for entry in recent_open_short_list]) or short_qty <= 0):
                                huFu.mix_place_plan_order(symbol, marginCoin, cent_qty, order[0], 'limit', trigger_price, "market_price", executePrice=order[1], clientOrderId=order[4],presetTakeProfitPrice=order[2], presetStopLossPrice=sl, reduceOnly=False)
                                logger.info("一垒就交给我了!⛳️  击打方向: %s ,击打点位: %s, 得分点: %s,失分点: %s ,编号: %s,得分圈: %s,失分圈: %s,手数 %f",order[0],order[1],order[2],sl,order[4],tp_delta,sl_delta,cent_qty)   

                        except Exception as e:
                            logger.debug(f"An unknown error occurred in mix_place_plan_order() ,orderOid(): {e} {order[4]}")
        return orders


    def record(self,current_price,pos,orders,track_orders,debug_mode):
        long_info  = [float(pos[0]["total"]),float(pos[0]['averageOpenPrice']),pos[0]['achievedProfits'],pos[0]['unrealizedPL']]
        short_info = [float(pos[1]["total"]),float(pos[1]['averageOpenPrice']),pos[1]['achievedProfits'],pos[1]['unrealizedPL']]
        if debug_mode:
            print(long_info)
            print(short_info)
        delta = 0
        if short_info[0] > 0:
            delta = short_info[1] - current_price
            logger.warning("SVS队员已上垒接球反击 : %f ,正在得分 :%f",short_info[1],delta)
        if long_info[0] > 0:
            delta = current_price - long_info[1]
            logger.warning("LOL队员已上垒接球反击 : %f ,正在得分 :%f",long_info[1],delta)

        for ft_orders in orders:
            for order in ft_orders:
                entry = order[1]
                label = order[4]
                if is_approximately_equal(short_info[1],entry)   or is_approximately_equal(long_info[1],entry):
                    logger.warning("球员记分,编号: %s, 进场位 %f, 得分圈%f",label,entry,delta)


        for order in track_orders:
                entry = order[1]
                label = order[4]
                if is_approximately_equal(short_info[1],entry)   or is_approximately_equal(long_info[1],entry):
                    logger.warning("球员记分,编号: %s, 进场位 %f, 得分圈%f",label,entry,delta)

    def base_run(self,current_price,pos,huFu,super_mode,consolidating,debug_mode,area):
        # a垒 ,36 开始,保一半
        a_base = 36
        # b垒 ,72 开始,保一半 
        if super_mode:
            a_base = a_base * 2
        long_info  = [float(pos[0]["total"]),float(pos[0]['averageOpenPrice']),pos[0]['achievedProfits'],pos[0]['unrealizedPL']]
        short_info = [float(pos[1]["total"]),float(pos[1]['averageOpenPrice']),pos[1]['achievedProfits'],pos[1]['unrealizedPL']]
        delta = 0
        new_long_sl = 0
        new_short_sl = 0

        if short_info[0] > 0:
            if consolidating:
                if not debug_mode:
                    huFu.mix_place_order(symbol,'USDT',short_info[0],'close_short','market',reduceOnly=True)
            if area != '':
                if area == 'premuim':
                    a_base = a_base * 2
            delta = short_info[1] - current_price
            if delta >= a_base:
                new_sl_point_delta = delta / 2
                new_short_sl = round(short_info[1] - new_sl_point_delta)
                ## move sl to new_short_sl
        if long_info[0] > 0:
            if consolidating:
                if not debug_mode:
                    huFu.mix_place_order(symbol,'USDT',short_info[0],'close_short','market',reduceOnly=True)
            if area != '':
                if area == 'premuim':
                    a_base = a_base * 2
            delta = current_price - long_info[1]
            if delta >= a_base:
                new_sl_point_delta = delta / 2
                new_long_sl = round(long_info[1] + new_sl_point_delta)
                ## move sl to new_long_sl


        try:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
            for plan in data:
                if plan['planType'] == 'loss_plan':
                    if plan['side'] == 'close_long' and new_long_sl != 0:
                        if new_long_sl > float(plan['triggerPrice']):
                            ## modifiy the sl
                            try:
                                size = plan['size']
                                if not debug_mode:
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                                    huFu.mix_place_stop_order(symbol, marginCoin, new_long_sl, 'loss_plan', 'long',triggerType='fill_price', size=size, rangeRate=None)      
                                logger.warning("LOL队员已在 %f 上垒击球,正在跑垒,得分区不断扩大,新失分区 : %f ",long_info[1],new_long_sl)

                            except Exception as e:
                                logger.warning(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_sl} ,{e}")
                            
                    elif plan['side'] == 'close_short' and new_short_sl != 0:
                        if new_short_sl < float(plan['triggerPrice']):
                            ## modifiy the sl
                            try:
                                size = plan['size']
                                if not debug_mode:
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                                    huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=size, rangeRate=None)                            
                                logger.warning("SVS队员已在 %f 上垒击球,正在跑垒,得分区不断扩大,新失分区 : %f ",short_info[1],new_short_sl)

                            except Exception as e:
                                logger.warning(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")

        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

    def consolidation(self,last_klines,dtrend):
        # 如果当前价格往前8根15m k range<=30,判定为巩固, 不做单,休息3h
        trend = ''
        klines = last_klines[-8:]
        klines = np.array(object=klines, dtype=np.float64)
        high = klines[:, 2]
        low = klines[:, 3]

        # 找到最高点和最低点的值和索引
        highest_index = np.argmax(high)
        lowest_index = np.argmin(low)

        # 判断最高点是否先出现
        if highest_index < lowest_index:
            trend = "bear"
        else:
            trend = "bull"

        delta = max(high) - min(low)
        if delta <=30:
            logger.warning("比赛评论员: 看起来双方打得难舍难分,比赛进入僵持阶段 🪵 (%f)",delta)
            return True
        else:
            if 30 < delta <= 100:
                note = '看起来形势不错,相当勇猛'
            if 100 < delta:
                note = '正在大杀特杀,势不可挡'
            if trend == 'bear':

                if dtrend[-1] == 'bull' or dtrend[-1] == 'reversal-bull' or dtrend[-1] == 'bull_pullback':
                    logger.warning("比赛评论员: S队 %s (%f),不过看起来L队大优势依旧在",note,delta)
                else:
                    logger.warning("比赛评论员: S队 %s (%f)",note,delta)
            elif trend == 'bull':
                if dtrend[-1] == 'bear' or dtrend[-1] == 'reversal-bear' or dtrend[-1] == 'bear_pullback':
                    logger.warning("比赛评论员: L队 %s (%f),不过看起来S队大优势依旧在",note,delta)
                else:
                    logger.warning("比赛评论员: L队 %s (%f)",note,delta)
            return False

    def earn_or_loss(self,huFu):
        startTime = get_previous_day_timestamp()
        endTime = get_previous_minute_timestamp()
        orders = huFu.mix_get_history_orders(symbol, startTime, endTime, 100, lastEndId='', isPre=False)['data']['orderList']
        loss_list = []
        loss_time_list = []
        loss_side_list = []
        total_profits = 0
        recent_open_long_list = []
        recent_open_short_list = []

        for order in orders:
            if float(order['totalProfits']) < 0:
                uTime = timestamp_to_time(float(order['uTime'])).strftime("%Y-%m-%d %H:%M:%S")
                if order['side'] == 'close_long':
                    entry = float(order['priceAvg']) - float(order['totalProfits']) / float(order['size']) 
                elif order['side'] == 'close_short':
                    entry = float(order['priceAvg']) + float(order['totalProfits']) / float(order['size']) 
                loss_time_list.append(order['uTime'])
                loss_list.append([uTime,entry])
                loss_side_list.append(order['side'])
            total_profits += order['totalProfits']
            if order['side'] == 'open_long' and order['state'] == 'filled':
                 recent_open_long_list.append([order['size'],float(order['priceAvg'])])
            if order['side'] == 'open_short' and order['state'] == 'filled':
                 recent_open_short_list.append([order['size'],float(order['priceAvg'])])


        loss_list = extract_recent_data(loss_list)
        count = loss_price_count(loss_list)
        print(count)

        if count < 2:
            return True,None,None,total_profits,recent_open_long_list,recent_open_short_list

        if loss_time_list != []:
            stop_loss_time = loss_time_list[0]
            loss_side = loss_side_list[0]
            return is_more_than_1hours(stop_loss_time),stop_loss_time,loss_side,total_profits,recent_open_long_list[:5],recent_open_short_list[:5]
        else:
            return True,None,None,total_profits,recent_open_long_list,recent_open_short_list
   
    def mayber_reversal(self,last_klines):
        klines = last_klines[-2:]
        klines = np.array(object=klines, dtype=np.float64)
        high = klines[:, 2]
        low = klines[:, 3]

        delta = max(high) - min(low)
        if delta <=15:
            logger.warning("看起来趋势可能要反转哦 ~ (%f)",delta)
            return True
        else:
            return False

    def reversal_wait(self,old,dtrend,debug_mode):
        new = check_string_type(dtrend[-1])
        if debug_mode:
            print('old',old)
            print('new',new)
        if old != '' and new != '':
            if old != new:
                return True,new
        else:
            return False,new

    def dis_or_pre(self,legs,current_price):
        last_leg = legs[-1]
        middle = (last_leg[1] + last_leg[2])/2
        middle_up = ((max(last_leg[1],last_leg[2]) + middle) /2 + middle) /2
        middle_down = (min(last_leg[1],last_leg[2]) + middle) /2
        print('midele',middle_up,middle_down)
        if current_price >= middle_up:
            return 'premuim'
        if current_price <= middle_down:
            return 'discount'
        else:
            return ''


def start(hero,symbol,marginCoin,debug_mode,fix_mode,fix_tp,base_qty,base_sl,max_qty,super_mode,init_fund,loss_ratio,loss_aum,lever_mark_mode,balance_rate,hand_mode):
    old = ''
    bb = BaseBall()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    if not debug_mode:
        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
                ## clear all open orders
            huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
        if not hand_mode:
            try:
                data = huFu.mix_get_open_order('BTCUSDT_UMCBL')['data']
                if data != []:
                    huFu.mix_cancel_all_orders ('UMCBL', marginCoin)
            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_cancel_all_orders(): {e}")

    logger.critical("三")
    time.sleep(1)
    logger.critical("二")
    time.sleep(1)
    logger.critical("一")
    time.sleep(1)
    logger.critical("比赛开始 🏎️  🏎️ 🏎️ 🏎️🏎️ !!!")

    while True:
        if lever_mark_mode:
            rsm = Risk_manager(init_fund,loss_ratio,loss_aum,balance_rate)
            try :
                dex = huFu.mix_get_accounts(productType='UMCBL')['data'][0]['usdtEquity']
                base_qty = rsm.get_current_loss_ratio(float(dex),base_sl)
                if rsm.balance_rate > 0:
                    dex_spot = huFu.spot_get_account_assets(coin='USDT')['data'][0]['available']

                    to_where,amount = rsm.rebalance(round(float(dex)),round(float(dex_spot)))
                    if to_where != '':
                        if not debug_mode:
                            if to_where == 'to_future':
                                huFu.spot_transfer('spot', 'mix_usdt', amount, 'USDT', clientOrderId=None)
                            elif to_where == 'to_spot':
                                huFu.spot_transfer('mix_usdt','spot', amount, 'USDT', clientOrderId=None)
                        logger.warning("平衡获利: %s %f",to_where,amount)
            except Exception as e:
                logger.debug(f"An unknown error occurred in rebalance(): {e}")




        try:
            result = huFu.mix_get_market_price(symbol)
            current_price = float(result['data']['markPrice'])
            logger.info("裁判播报员: ⚾️ 坐标 %s ",current_price)
        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_get_market_price(): {e}")

        max_pains = get_max_pains()
        if max_pains != None:
            rencent_max_pain = max_pains[0]
        else:
            rencent_max_pain = None
        if rencent_max_pain != None:
            if current_price >= float(rencent_max_pain[1]):
                notice = '当前 ⚾️ 坐标位置 '+str(current_price)+' 大于最终得分区,LOL队员请小心~'
            else:
                notice = '当前 ⚾️ 坐标位置 '+str(current_price)+' 小于最终得分区,SVS队员请小心~'

            time_remaining = time_until_nearest_8am()
            remain_notice = '本日比赛结束倒计时: ' + time_remaining
            date_type = get_date_type(rencent_max_pain[0])

            current_session, ltime_remaining, time_until_next_session = get_time_range()

            logger.warning("\n %s %s ,本场比赛还有 %s 结束, 距离下场区域赛还有 %s 开始",date_type,current_session, ltime_remaining, time_until_next_session)
            logger.warning("最近 options 临近时间 %s, options 最终目标得分区 %s , %s , %s",rencent_max_pain[0],rencent_max_pain[1],remain_notice,notice)

            if len(max_pains) > 5:
                logger.warning("稍后比赛临近时间及得分区:")
                for i in range(1, 4, 2):
                    max_pain_pair = max_pains[i:i+2]
                    logger.warning("\t \t %s", ' '.join(str(p) for p in max_pain_pair))

        if not debug_mode:
            try:
                data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

            if data != []:
                    ## clear all open orders
                try:
                    huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_cancel_all_trigger_orders(): {e}")
            if not hand_mode:
                try:
                    data = huFu.mix_get_open_order('BTCUSDT_UMCBL')['data']
                    if data != []:
                        huFu.mix_cancel_all_orders ('UMCBL', marginCoin)
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_cancel_all_orders(): {e}")
        startTime = get_previous_month_timestamp()
        endTime = get_previous_minute_timestamp()
        trend = []
        ft_list = ['15m','30m','1H','4H','1D']
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
            r,b = bb.zigzag(klines=klines, min_size=0.0055, percent=True)
            if ft == '15m':
                last_klines = klines
            if ft == '1H':
                one_H_legs = r
            b.insert(0,ft)
            trend.append(b)
            time.sleep(0.3)

        dtrend = bb.determine_trend(one_H_legs)
        one_H_legs = one_H_legs[1:]
        legs = [[dtrend] + one_H_legs[1:] for dtrend, one_H_legs in zip(dtrend, one_H_legs)]
        last_legs = [leg for leg in legs if leg[0] != 'bull_pullback' and leg[0] != 'bear_pullback']

        if debug_mode:
            print(one_H_legs)
            print(dtrend)

            print(last_legs)

        # reversal 
        if is_wednesday_or_thursday():
            fix_base_qty = base_qty *2 
            week_notice = '热赛区'        
        else:
            fix_base_qty = base_qty
            week_notice = ''

        if is_reversal_time() or bb.mayber_reversal(last_klines) or is_nfp_time():
            fix_base_qty = round(fix_base_qty / 4,3)
            re_notice = '反转区'
        else:
            fix_base_qty = fix_base_qty
            re_notice = '非反转区'
        area = bb.dis_or_pre(last_legs,current_price)

        logger.warning("当前是 %s %s , 调整后手数 :%s ,所处区域 %s ",week_notice,re_notice,fix_base_qty,area)

        reversal_w,old = bb.reversal_wait(old,dtrend,debug_mode)
        if reversal_w:
            logger.warning("交换球权 ,大家 休息5min 缓缓 ~")
            time.sleep(5*60)

        consolidating = bb.consolidation(last_klines,dtrend)
        orders = bb.advortise(trend,fix_mode,fix_tp)
        try:
            result = huFu.mix_get_single_position(symbol,marginCoin)
            pos = result['data']

        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_get_single_position(): {e}")
        
        long_qty = float(pos[0]["total"])
        short_qty = float(pos[1]["total"])

        if not trading_time():
            logger.warning("球馆休息时间 ~ ~")

        loss_away,stop_loss_time,loss_side,total_profits,recent_open_long_list,recent_open_short_list = bb.earn_or_loss(huFu)
        out_max_qty = max_qty * 2
        if long_qty <= out_max_qty and short_qty<= out_max_qty and not consolidating and loss_away and trading_time():
            bb.batch_orders(orders,huFu,marginCoin,fix_base_qty,debug_mode,base_sl,current_price,super_mode,dtrend,recent_open_long_list,recent_open_short_list,long_qty,short_qty)
        if not super_mode and not consolidating and loss_away and trading_time():
            track_orders = bb.on_track(last_legs,huFu,marginCoin,fix_base_qty,debug_mode,base_sl,pos,max_qty,dtrend,recent_open_long_list,recent_open_short_list,long_qty,short_qty,orders)

        time.sleep(0.3)
        batch_refresh_interval = 2
        if super_mode:
            batch_refresh_interval = 60
        for i in range(batch_refresh_interval):
            for k in range(60):
                time.sleep(1.5)
                try:
                    result = huFu.mix_get_single_position(symbol,marginCoin)
                    pos = result['data']

                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_get_single_position(): {e}")

                try:
                    result = huFu.mix_get_market_price(symbol)
                    current_price = float(result['data']['markPrice'])
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_get_market_price(): {e}")

                bb.base_run(current_price,pos,huFu,super_mode,consolidating,debug_mode,area)
                time.sleep(1.5)
            logger.info("裁判播报员: ⚾️ 坐标 %s ",current_price)

            if not loss_away:
                winner = ''
                if loss_side == 'close_long':
                    winner = 'SVS队'
                elif loss_side == 'close_short':
                    winner = 'LOL队'
                remaining_time = remaining_time_to_1_hours(stop_loss_time)
                logger.warning("半场赛结束 ~ 🚩胜方 %s ",winner)
                logger.warning("球员们休息调整中 ☕️~ 距离下半场比赛开始还有:  %s",remaining_time)

            if not debug_mode:
                try:
                    data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

                if data != []:
                    for order in data:
                        if '_' not in order['clientOid']:
                        ## clear all open orders
                            try:
                                huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'], 'normal_plan')
                            except Exception as e:
                                logger.debug(f"An unknown error occurred in mix_cancel_plan_order(): {e}")
                if not hand_mode:
                    try:
                        data = huFu.mix_get_open_order('BTCUSDT_UMCBL')['data']
                        if data != []:
                            huFu.mix_cancel_all_orders ('UMCBL', marginCoin)
                    except Exception as e:
                        logger.debug(f"An unknown error occurred in mix_cancel_all_orders(): {e}")
            if not super_mode and not consolidating and loss_away and trading_time():
                track_orders = bb.on_track(last_legs,huFu,marginCoin,fix_base_qty,debug_mode,base_sl,pos,max_qty,dtrend,recent_open_long_list,recent_open_short_list,long_qty,short_qty,orders)

            if super_mode or consolidating or not loss_away or not trading_time():
                track_orders = []
            bb.record(current_price,pos,orders,track_orders,debug_mode)

        if consolidating:
            logger.warning("请注意!!! 准备休息,开始修理场地 ~~~~")
            time.sleep(1800)

        if is_less_than_10_minutes(time_remaining):
            if total_profits >= 0:
                note = '今天又是个大满贯!!!'
            elif total_profits < 0:
                note = '请选手们不要气馁,再接再厉 ~'
            logger.critical("今日比赛临近末尾,当前总得分: %s ,%s",total_profits,note)
            delta = abs(current_price - rencent_max_pain[1])
            logger.critical("赛末通告 - 最终目标区: %s ,当前 ⚾️ 位置: %f , 差值 %f",rencent_max_pain[1],current_price,delta)
             


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')
    parser.add_argument('-lm', '--lever_mark_mode', action='store_true', default=True, help='Enable lever_mark_mode')
    parser.add_argument('-hm', '--hand_mode', action='store_true', default=False, help='Enable hand_mode')


    parser.add_argument('-fp', '--fix_tp_point', default=88,help='fix_tp_point')
    parser.add_argument('-bsl', '--base_sl', default=88,help='base_sl')
    parser.add_argument('-bq', '--base_qty', default=0.05,help='base_qty')
    parser.add_argument('-mxq', '--max_qty', default=1.5,help='max_qty')
    parser.add_argument('-if', '--init_fund', default=5000,help='init_fund')
    parser.add_argument('-lr', '--loss_ratio', default=0.01,help='loss_ratio')
    parser.add_argument('-aum', '--AUM', default=0.2,help='AUM')
    parser.add_argument('-br', '--balance_rate', default=0.5,help='balance_rate')


    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode
    fix_mode = args.fix_tp_mode
    super_mode = args.super_mode
    lever_mark_mode = args.lever_mark_mode
    hand_mode = args.hand_mode

    fix_tp = float(args.fix_tp_point)
    base_qty = float(args.base_qty)
    base_sl = float(args.base_sl)
    max_qty = float(args.max_qty)

    init_fund = float(args.init_fund)
    loss_ratio = float(args.loss_ratio)
    loss_aum = float(args.AUM)
    balance_rate = float(args.balance_rate)

    logger = get_logger(heroname+'_record.log')

    config = get_config_file()
    hero = config[heroname]
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    logger.info("让场子热起来吧🔥！ 新一场棒球比赛即将开始⚾️～")
    start(hero,symbol,marginCoin,debug_mode,fix_mode,fix_tp,base_qty,base_sl,max_qty,super_mode,init_fund,loss_ratio,loss_aum,lever_mark_mode,balance_rate,hand_mode)