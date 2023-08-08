from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *

class SMC():
    def __init__(self) -> None:
        pass

    def process_kline_data(self,kline_data):
        df = pd.DataFrame(kline_data, columns=['time', 'open', 'high', 'low', 'close', 'volume','usdt_volume'])
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['open'] = pd.to_numeric(df['open'])
        df['close'] = pd.to_numeric(df['close'])

        # Convert 'time' column to datetime and set it as the index
        df['utc_time'] = pd.to_datetime(df['time'].astype(int), unit='ms')

        # Add 'status' column based on 'close' and 'open' values
        df['status'] = 'star'
        df.loc[df['close'] > df['open'], 'status'] = 'bull'
        df.loc[df['close'] < df['open'], 'status'] = 'bear'
        
        df['delta'] = df['high'] - df['low']

        # Move 'utc_time' column to the front
        df = df[['utc_time', 'time','open', 'high', 'low', 'close', 'delta','volume', 'status']]
        
        return df

    def swings(self,*, klines, min_size, percent):
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
        swing_points = [item[1] for item in sorted_price]
        marked_swing_points = []
        
        for i in range(len(swing_points)):
            if i == 0:
                continue
            elif i == 1:
                if swing_points[i] > swing_points[i - 1]:
                    marked_swing_points.append((swing_points[i - 1], 'L'))
                    marked_swing_points.append((swing_points[i], 'H'))
                else:
                    marked_swing_points.append((swing_points[i - 1], 'H'))
                    marked_swing_points.append((swing_points[i], 'L'))
            else:
                if swing_points[i] > swing_points[i - 1]:
                    if swing_points[i] > swing_points[i - 2]:
                        marked_swing_points.append((swing_points[i], 'HH'))
                    else:
                        marked_swing_points.append((swing_points[i], 'HL'))
                else:
                    if swing_points[i] > swing_points[i - 2]:
                        marked_swing_points.append((swing_points[i], 'LH'))
                    else:
                        marked_swing_points.append((swing_points[i], 'LL'))
        
        return marked_swing_points

    def get_inside_bars(self,klines):
        def is_inside_bar(current_high, current_low, prev_high, prev_low):
            # 判断当前蜡烛是否是Inside Bar
            if current_high <= prev_high and current_low >= prev_low:
                return True
            else:
                return False

        klines['inside_bar'] = 0

        for i in range(1, len(klines)):
            current_high = float(klines.at[i, 'high'])
            current_low = float(klines.at[i, 'low'])
            current_open = float(klines.at[i, 'open']) 
            current_close = float(klines.at[i, 'close'])

            prev_high = float(klines.at[i - 1, 'high'])
            prev_low = float(klines.at[i - 1, 'low'])

            if is_inside_bar(current_high, current_low, prev_high, prev_low):
                upper_shadow = abs(current_high - max(current_open, current_close))
                lower_shadow = abs(min(current_open, current_close) - current_low)
                shadow_length = max(upper_shadow, lower_shadow)

                entity_delta = abs(float(klines.at[i, 'open']) - float(klines.at[i, 'close']))

                delta = current_high - current_low
                if delta >= 15 and delta > (entity_delta + 3) and entity_delta > 5 and shadow_length < entity_delta * 2.5:
                    klines.loc[i, 'inside_bar'] = 1
        klines = klines[['utc_time', 'time','open', 'high', 'low', 'close', 'delta','volume', 'status','inside_bar']]
        filtered_df = klines[klines['inside_bar'] == 1]

        return filtered_df
    
    def mark_swing_points(self,swing,klines):
        def mark_near_index(l_label,inside_bar_indices,poi_decr):

            derc_indices = []
            for label in l_label:
                # 找到 'swing_point' 列为 'LL' 的索引
                indices = klines[klines['swing_point'] == label].index
                derc_indices.append(indices)

            for indices in derc_indices:
                if not indices.empty:
                    for ele in indices:
                        # 找到 'swing_point' 为 'LL' 并且距离最近的 'inside_bar' 为 1 的索引
                        nearest_inside_bar_index = min(inside_bar_indices, key=lambda x: abs(x - ele))
                        delta = abs(ele - nearest_inside_bar_index)
                        if delta <= 5:
                        # 标记 'poi' 列为 'high'
                            klines.loc[nearest_inside_bar_index, 'poi'] = poi_decr

            
        klines['swing_point'] = ''
        klines['poi'] = ''
        for point in swing:
            if point[1] == 'L' or point[1] == 'LL' or point[1] == 'LH':
                klines.loc[klines['low'] == point[0] , 'swing_point'] = point[1]
            if point[1] == 'H' or point[1] == 'HL' or point[1] == 'HH':
                klines.loc[klines['high'] == point[0] , 'swing_point'] = point[1]
        # 找到 'inside_bar' 为 1 的索引
        inside_bar_indices = klines[klines['inside_bar'] == 1].index
        l_label = ['LL','LH','L']
        poi_decr = 'high_buy'
        mark_near_index(l_label,inside_bar_indices,poi_decr)

        l_label = ['HL','HH','H']
        poi_decr = 'high_sell'
        mark_near_index(l_label,inside_bar_indices,poi_decr)

        return klines

    def mark_reversal_bar(self,df):
        # 初始化reversal_bar列为''
        df['reversal_bar'] = ''

        # 判断是否为reversal_bar并赋值
        for i in range(1, len(df)):
            current_high = df.at[i, 'high']
            current_low = df.at[i, 'low']
            prev_high = df.at[i - 1, 'high']
            prev_low = df.at[i - 1, 'low']
            close = df.at[i, 'close']
            open = df.at[i, 'open']

            if current_high > prev_high and current_low < prev_low:
                if close < open:
                    df.at[i, 'reversal_bar'] = 'reversal_sell'
                else:
                    df.at[i, 'reversal_bar'] = 'reversal_buy'

        return df

    def inside_order_adv(self,df,filtered_df,current_price):
        order_list = []
        filtered_df['middle'] = filtered_df[['open', 'close']].mean(axis=1).apply(lambda x: round(x * 2) / 2)

        for i, row in filtered_df.iterrows():
            if current_price < row['middle']:
                print(f"Index: {i}")
                derc = 'open_short'
                entry_m = row['middle']
                entry_edge = row['low']
                sl = df.at[i - 1, 'high']
                sl_m_delta = abs(entry_m - sl)
                sl_edge_delta = abs(entry_edge - sl)
                tp_m = entry_m - sl_m_delta * 2
                tp_edge = entry_edge - sl_edge_delta * 2
                order_m = [derc,entry_m,tp_m,sl,sl_m_delta]
                order_edge = [derc,entry_edge,tp_edge,sl,sl_edge_delta]
                order_list.append(order_m)
                order_list.append(order_edge)
                print(f"entry_m: {order_m}")
                print(f"entry_edge: {order_edge}")

            if current_price > row['middle']:
                print(f"Index: {i}")
                derc = 'open_long'

                entry_m = row['middle']
                entry_edge = row['high']
                sl = df.at[i - 1, 'low']
                sl_m_delta = abs(entry_m - sl)
                sl_edge_delta = abs(entry_edge - sl)
                tp_m = entry_m + sl_m_delta * 2
                tp_edge = entry_edge + sl_edge_delta * 2
                order_m = [derc,entry_m,tp_m,sl,sl_m_delta]
                order_edge = [derc,entry_edge,tp_edge,sl,sl_edge_delta]
                print(f"entry_m: {order_m}")
                print(f"entry_edge: {order_edge}")
                order_list.append(order_m)
                order_list.append(order_edge)
            
        return order_list
        

    def place_batch_orders(self,orders,huFu,base_qty):
        #  odr[0]=derc     odr[1]=entry     odr[2]=tp   odr[3]=sl

        for odr in orders:
            try:

                huFu.mix_place_plan_order(symbol, marginCoin, base_qty ,odr[0], 'limit', odr[1], "market_price", executePrice=odr[1],presetTakeProfitPrice=odr[2], presetStopLossPrice=odr[3], reduceOnly=False)
                print("place",odr)
            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_place_plan_order(): {e}")


    def get_net_orders(self,huFu,order_list):
        startTime = get_previous_hour_timestamp_ex()
        endTime = get_previous_minute_timestamp()
        orders = huFu.mix_get_history_orders(symbol, startTime, endTime, 100, lastEndId='', isPre=False)['data']['orderList']

        recent_open_price_list = []

        for order in orders:
            if order['side'] == 'open_long' and order['state'] == 'filled':
                 recent_open_price_list.append(float(order['priceAvg']))
            if order['side'] == 'open_short' and order['state'] == 'filled':
                 recent_open_price_list.append(float(order['priceAvg']))
        st = timestamp_to_time(startTime)
        et = timestamp_to_time(endTime)

        for ord in order_list:
            if is_approx_equal_to_any(ord[1],recent_open_price_list):
                order_list = [order for order in order_list if order != ord]
        print(st," to ",et," recent_open_price_list",recent_open_price_list)
        try:
            data_list = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")
        execute_prices = [float(data['executePrice']) for data in data_list]
        # 输出结果
        for ord in order_list:
            if is_approx_equal_to_any(ord[1],execute_prices,0):
                order_list = [order for order in order_list if order != ord]
        print("net order list",order_list)
        return order_list


## inside bar 过5根bar后开始挂单,挂在close处， 入场为h+l /2 ，止损放在前一根另一边,第72根失效（不包含inside_bar）
## 止损两次即失效

def start(hero,symbol,marginCoin,debug_mode):
    pd.set_option('display.max_rows', 100)

    smc = SMC()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    inside_bar_orders(smc,symbol,marginCoin,debug_mode,base_qty,huFu)



    # startTime = get_previous_month_timestamp()
    # endTime = get_previous_minute_timestamp()
    # x = 3

    # startTime = get_previous_x_timestamp(x+1)

    # endTime = get_previous_x_timestamp(x)
    # trend = []
    # ft_list = ['5m','15m','30m','1H','4H','1D']
    # ft_list = ['5m','15m']

    # last_legs = []
    # last_klines = []
    # for ft in ft_list:

    #     max_retries = 3
    #     retry_delay = 1  # 延迟时间，单位为秒
    #     retry_count = 0
    #     klines = []

    #     while not klines and retry_count < max_retries:
    #         try:
    #             klines = huFu.mix_get_candles(symbol, ft, startTime, endTime)
    #         except Exception as e:
    #             logger.debug(f"An unknown error occurred in mix_get_candles(): {e} ,{ft}")
            
    #         if not klines:
    #             retry_count += 1
    #             print("再来一次")
    #             time.sleep(retry_delay)
    #     if ft == '5m':
    #         data = smc.process_kline_data(klines)
    #         inside = smc.get_inside_bars(data)
    #         # 使用 Pandas 进行比较和判断
    #         current_price = 29000
    #         order_list = smc.inside_order_adv(data,inside,current_price)      
    #         current_price = 30000
    #         smc.inside_order_adv(data,inside,current_price)   
            # swing = smc.swings(klines=klines, min_size=0.0015, percent=True)
            # print('swing',swing)
            # mal = smc.mark_swing_points(swing,data)

            # filtered_df = mal[mal['poi'] != '']
            # # print(filtered_df)
            # # print()

            # mal = smc.mark_reversal_bar(mal)
            # filtered_df = mal[mal['reversal_bar'] != '']
            # # print(filtered_df)
            # print(mal)

        #inside = smc.get_inside_bars(klines)
        #print(inside)
        # if ft == '15m':
        #     swing = smc.swings(klines=klines, min_size=0.0055, percent=True)
        #     print(swing)
        #     mal = smc.mark_swing_points(swing,data)
        #     print(mal)
        #     filtered_df = mal[mal['swing_point'] != '']
        #     print(filtered_df)
        #     filtered_df = mal[mal['poi'] != '']
        #     print(filtered_df)


def inside_bar_orders(smc,symbol,marginCoin,debug_mode,base_qty,huFu):
    while True:
        x = 6
        startTime = get_previous_x_hour_timestamp(x)
        endTime = get_minute_timestamp()
        ft_list = ['5m','15m']
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
            
            if ft == '5m':
                df_klines_5m = smc.process_kline_data(klines)
                df_klines_5m.drop(df_klines_5m.tail(5).index, inplace=True)
                inside = smc.get_inside_bars(df_klines_5m)

            if ft == '15m':
                data_15 = smc.process_kline_data(klines)
                data_15.drop(data_15.tail(5).index, inplace=True)

                inside_15 = smc.get_inside_bars(data_15)

        # cancel all orders
        try:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
            if data != []:
                    ## clear all open orders
                ## if orders in open_orders 
                huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")


        try:
            data = huFu.mix_get_open_order('BTCUSDT_UMCBL')['data']
            if data != []:
                huFu.mix_cancel_all_orders ('UMCBL', marginCoin)
        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_cancel_all_orders(): {e}")
        

        batch_refresh_interval = 3

        for i in range(batch_refresh_interval):
            for k in range(2):             # 60
                time.sleep(15)
                try:
                    result = huFu.mix_get_market_price(symbol)
                    current_price = float(result['data']['markPrice'])
                    logger.info("裁判播报员: ⚾️ 坐标 %s ",current_price)
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_get_market_price(): {e}")
                order_list = smc.inside_order_adv(df_klines_5m,inside,current_price) 
                order_list_15 = smc.inside_order_adv(data_15,inside_15,current_price) 
                if order_list != []:
                    order_list = smc.get_net_orders(huFu,order_list)
                if order_list_15 != []:
                    order_list_15 = smc.get_net_orders(huFu,order_list_15)

                if order_list != [] or order_list_15 != []:

                    # place orders

                    if not debug_mode:
                        smc.place_batch_orders(order_list,huFu,base_qty)
                        smc.place_batch_orders(order_list_15,huFu,base_qty)

                time.sleep(15)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')

    parser.add_argument('-fp', '--fix_tp_point', default=88,help='fix_tp_point')
    parser.add_argument('-bsl', '--base_sl', default=88,help='base_sl')
    parser.add_argument('-bq', '--base_qty', default=0.01,help='base_qty')
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
