##


from pybitget import Client
import pandas as pd
import numpy as np
import argparse
from utils import *
import talib as ta

pd.set_option('display.max_rows', 100)


class SideBar():
    def __init__(self) -> None:
        pass
    

    def get_last_bar(self,symbol,huFu,ft):
        if ft == '1m':
            x = 2
        if ft == '5m':
            x= 8
        startTime = get_previous_x_hour_timestamp(x)
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
        return klines[-3:],klines
    
    def get_last_bar_x(self,symbol,huFu,ft):
        if ft == '1m':
            x = 2
        if ft == '5m':
            x= 8
        startTime = get_previous_x_hour_timestamp(x)
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
        return klines[-4:-1],klines

    def inside_outside(self,bars,klines):
        def confirm_bar(klines):
            def kvo(df, short_period, long_period, signal_period):
                df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
                df['sv'] = np.where(df['hlc3'].diff() >= 0, df['volume'], -df['volume'])
                # 计算KVO
                ema_short = ta.EMA(df['sv'], short_period)
                ema_long = ta.EMA(df['sv'], long_period)
                df['kvo'] = ema_short - ema_long

                df['signal'] = df['kvo'].ewm(span=signal_period).mean()
                return df
            
            def hma(period):
                wma_1 = df['close'].rolling(period//2).apply(lambda x: \
                np.sum(x * np.arange(1, period//2+1)) / np.sum(np.arange(1, period//2+1)), raw=True)
                wma_2 = df['close'].rolling(period).apply(lambda x: \
                np.sum(x * np.arange(1, period+1)) / np.sum(np.arange(1, period+1)), raw=True)
                diff = 2 * wma_1 - wma_2
                hma = diff.rolling(int(np.sqrt(period))).mean()
                return hma

            # Define column names
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']

            # Create a DataFrame from the data
            df = pd.DataFrame(klines, columns=columns)


            # Convert numeric columns to appropriate data types
            df[['timestamp','open', 'high', 'low', 'close', 'volume', 'turnover']] = df[['timestamp','open', 'high', 'low', 'close', 'volume', 'turnover']].apply(pd.to_numeric)
            
            # Convert timestamp column to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Calculate KVO
            short_period = 34  # Change this to your desired short period
            long_period = 55   # Change this to your desired long period
            signal_period = 13 # Change this to your desired signal period
            df = kvo(df, short_period, long_period, signal_period)

            # Calculate lsma
            period = 27
            df['hma'] = hma(period)

            last_row = df.iloc[-1].to_dict()
            open = last_row['open']
            close = last_row['close']
            kvo = last_row['kvo']
            lsma = last_row['hma']
            if close > open and kvo > 0 and lsma < close:
                return 'long'
            elif close < open and kvo < 0 and lsma > close:
                return 'short'
            else:
                return '' 

        def is_inside_bar(pre,current):
            if current[2] < pre[2] and current[3]> pre[3]:
                return True
            else:
                return False
        
        def is_outside_bar(pre,current):
            if current[2] > pre[2] and current[3] < pre[3]:
                return True
            else:
                return False
        derc = confirm_bar(klines)

        if is_inside_bar(bars[0],bars[1]):
            if is_outside_bar(bars[1],bars[2]) and derc == 'short':
                print("derc ",derc)
                return 'short'
        elif is_outside_bar(bars[0],bars[1]):
            if is_inside_bar(bars[1],bars[2]) and derc == 'long':
                print("derc ",derc)
                return 'long'  
        else:
            return ''

    def inside_outside_x(self,bars,klines):
        def confirm_bar(klines):
            def kvo(df, short_period, long_period, signal_period):
                df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
                df['sv'] = np.where(df['hlc3'].diff() >= 0, df['volume'], -df['volume'])
                # 计算KVO
                ema_short = ta.EMA(df['sv'], short_period)
                ema_long = ta.EMA(df['sv'], long_period)
                df['kvo'] = ema_short - ema_long

                df['signal'] = df['kvo'].ewm(span=signal_period).mean()
                return df
            def hma(period):
                wma_1 = df['close'].rolling(period//2).apply(lambda x: \
                np.sum(x * np.arange(1, period//2+1)) / np.sum(np.arange(1, period//2+1)), raw=True)
                wma_2 = df['close'].rolling(period).apply(lambda x: \
                np.sum(x * np.arange(1, period+1)) / np.sum(np.arange(1, period+1)), raw=True)
                diff = 2 * wma_1 - wma_2
                hma = diff.rolling(int(np.sqrt(period))).mean()
                return hma

            # Define column names
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']

            # Create a DataFrame from the data
            df = pd.DataFrame(klines, columns=columns)


            # Convert numeric columns to appropriate data types
            df[['timestamp','open', 'high', 'low', 'close', 'volume', 'turnover']] = df[['timestamp','open', 'high', 'low', 'close', 'volume', 'turnover']].apply(pd.to_numeric)
            
            # Convert timestamp column to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Calculate KVO
            short_period = 34  # Change this to your desired short period
            long_period = 55   # Change this to your desired long period
            signal_period = 13 # Change this to your desired signal period
            df = kvo(df, short_period, long_period, signal_period)

            # Calculate lsma
            period = 27
            df['hma'] = hma(period)

            last_row = df.iloc[-2].to_dict()
            open = last_row['open']
            close = last_row['close']
            kvo = last_row['kvo']
            lsma = last_row['hma']
            if close > open and kvo > 0 and lsma < close:
                return 'long'
            elif close < open and kvo < 0 and lsma > close:
                return 'short'
            else:
                return '' 

        def is_inside_bar(pre,current):
            if current[2] < pre[2] and current[3]> pre[3]:
                return True
            else:
                return False
        
        def is_outside_bar(pre,current):
            if current[2] > pre[2] and current[3] < pre[3]:
                return True
            else:
                return False
        derc = confirm_bar(klines)

        if is_inside_bar(bars[0],bars[1]):
            if is_outside_bar(bars[1],bars[2]) and derc == 'short':
                print("derc ",derc)
                return 'short'
        elif is_outside_bar(bars[0],bars[1]):
            if is_inside_bar(bars[1],bars[2]) and derc == 'long':
                print("derc ",derc)
                return 'long'  
        else:
            return ''




        # if bar[1] inside bar ; bar[2] outside ; sell
        # if bar[2] inside bar ; bar[1] outside ; buy

    def place_order(self,side,huFu,symbol,marginCoin,base_qty,trailing_delta,trailing_loss_mode,rangeRate,trailing_delta_mul,pyramid_mode):
        # tp long 12, tp short 15
        # sl long 24 , sl short 30
        if trailing_delta_mul != 1:
            tp_long_delta = trailing_delta
            tp_short_delta = trailing_delta
            protect_long_loss_delta = 350
            protect_short_loss_delta = 440
        else:
            tp_long_delta = 12 * trailing_delta
            tp_short_delta = 15 * trailing_delta
            protect_long_loss_delta = 24 * trailing_delta
            protect_short_loss_delta = 30 * trailing_delta
        
        protect_rangeRate = 0.01
        def qty_decide(huFu):
            max_retries = 3
            retry_delay = 1  # 延迟时间，单位为秒
            retry_count = 0
            dex = 0

            while dex == 0 and retry_count < max_retries:
                try :
                    dex = huFu.mix_get_accounts(productType='UMCBL')['data'][0]['usdtEquity']
                    return round(float(dex)/10000,3)
                except Exception as e:
                    logger.debug(f"An unknown error occurred in mix_get_single_position(): {e}")
                if dex == 0:
                    retry_count += 1
                    print("再来一次")
                    time.sleep(retry_delay)
      
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
                    if base_qty == 0:
                        qty = qty_decide(huFu)
                        base_qty = qty
                    # cancel all orders
                    try:
                        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
                        if data != []:
                            for order in data:
                                if order['planType'] == 'normal_plan':
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'normal_plan')
                                elif order['planType'] == 'track_plan':
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'track_plan')


                    except Exception as e:
                        logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

                    huFu.mix_place_order(symbol,'USDT',base_qty,'open_long','market',reduceOnly=False)
                    logger.info("open long")
                    # get pos price
                    result = huFu.mix_get_single_position(symbol,marginCoin)
                    trailing_protect_price = round(float(result['data'][0]["averageOpenPrice"]) - protect_long_loss_delta)
                    side = 'close_long'
                    huFu.mix_place_trailing_stop_order(symbol, marginCoin, trailing_protect_price, side, triggerType=None,size=base_qty, rangeRate=protect_rangeRate)
                    logger.info("entry at %s , trailing protect loss at %f , trailing protect delta is %f ",result['data'][0]['averageOpenPrice'],trailing_protect_price,protect_long_loss_delta)

                    if trailing_loss_mode:
                        trailing_price = round(float(result['data'][0]["averageOpenPrice"]) + tp_long_delta)
                        huFu.mix_place_trailing_stop_order(symbol, marginCoin, trailing_price, side, triggerType=None,size=base_qty, rangeRate=rangeRate)
                        logger.info(" trailing profit at %f , trailing delta is %f ",trailing_price,tp_long_delta)


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
                if short_qty == 0 or pyramid_mode:
                    if base_qty == 0:
                        qty = qty_decide(huFu)
                        base_qty = qty
                    if short_qty > base_qty * 5:
                        logger.warning("reach the max qty %f",base_qty * 5)
                        return
                    # cancel all orders
                    try:
                        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
                        if data != []:
                            for order in data:
                                if order['planType'] == 'normal_plan':
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'normal_plan')
                                elif order['planType'] == 'track_plan':
                                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'track_plan')


                    except Exception as e:
                        logger.debug(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

                    huFu.mix_place_order(symbol,'USDT',base_qty,'open_short','market',price='',reduceOnly=False)
                    logger.info("open short")
                    # get pos price
                    result = huFu.mix_get_single_position(symbol,marginCoin)
                    trailing_protect_price = round(float(result['data'][1]["averageOpenPrice"]) + protect_short_loss_delta)
                    side = 'close_short'
                    huFu.mix_place_trailing_stop_order(symbol, marginCoin, trailing_protect_price, side, triggerType=None,size=base_qty, rangeRate=protect_rangeRate)
                    logger.info("entry at %s , trailing protect loss at %f , trailing protect delta is %f ",result['data'][1]['averageOpenPrice'],trailing_protect_price,protect_short_loss_delta)

                    if trailing_loss_mode:
                        trailing_price = round(float(result['data'][1]["averageOpenPrice"]) - tp_short_delta)
                        huFu.mix_place_trailing_stop_order(symbol, marginCoin, trailing_price, side, triggerType=None,size=base_qty, rangeRate=rangeRate)
                        logger.info(" trailing profit at %f , trailing delta is %f ",trailing_price,tp_short_delta)

            except Exception as e:
                logger.debug(f"An unknown error occurred in mix_place_order(): {e}")
            

def start(hero,symbol,marginCoin,debug_mode,base_qty,super_mode,trailing_delta_mul,trailing_loss_mode,rangeRate,pyramid_mode):
    rvs = SideBar()
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    pre_lastest_bar = ''
    # last_1m = rvs.get_last_bar(symbol,huFu,'1m')
    while True:
        try:
            result = huFu.mix_get_market_price(symbol)
            current_price = float(result['data']['markPrice'])
        except Exception as e:
            logger.debug(f"An unknown error occurred in mix_get_market_price(): {e}")

        trailing_delta = round(trailing_delta_mul * current_price * 0.0005)

        if super_mode:
        # print(last_1m)
            last_5m_bars,all_bars = rvs.get_last_bar(symbol,huFu,'5m')

            side = rvs.inside_outside(last_5m_bars,all_bars)
            lastest_bar = last_5m_bars[-2]

        else:
            last_5m_bars,all_bars = rvs.get_last_bar_x(symbol,huFu,'5m')

            side = rvs.inside_outside_x(last_5m_bars,all_bars)
            lastest_bar = last_5m_bars[-1]


        if lastest_bar == pre_lastest_bar:
            continue
        else:
            pre_lastest_bar = lastest_bar
        print("new bar:",timestamp_to_time(int(pre_lastest_bar[0])),pre_lastest_bar)
        if debug_mode:
            print(trailing_delta)
            for i in last_5m_bars:
                print(timestamp_to_time(int(i[0])) , i)
            print('side:',side)

        if not debug_mode:
            if side != '':
                rvs.place_order(side,huFu,symbol,marginCoin,base_qty,trailing_delta,trailing_loss_mode,rangeRate,trailing_delta_mul,pyramid_mode)

        time.sleep(10)


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')
    parser.add_argument('-tl', '--trailing_loss_mode', action='store_true', default=False, help='Enable trailing_loss')
    parser.add_argument('-pm', '--pyramid_mode', action='store_true', default=False, help='Enable pyramid_mode')

    parser.add_argument('-pr', '--pair', default='BTCUSDT_UMCBL',help='pair')
    parser.add_argument('-bq', '--base_qty', default=0,help='base_qty')
    parser.add_argument('-tm', '--trailing_delta_mul', default=1,help='trailing_delta_mul')
    parser.add_argument('-rr', '--rangeRate', default=0.01,help='rangeRate')

    


    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode
    super_mode = args.super_mode
    trailing_loss_mode = args.trailing_loss_mode
    pyramid_mode = args.pyramid_mode

    base_qty = float(args.base_qty)
    trailing_delta_mul = float(args.trailing_delta_mul)
    rangeRate = float(args.rangeRate)
    symbol = args.pair

    logger = get_logger(heroname+'_record.log')

    config = get_config_file()
    hero = config[heroname]
    marginCoin = 'USDT'
    start(hero,symbol,marginCoin,debug_mode,base_qty,super_mode,trailing_delta_mul,trailing_loss_mode,rangeRate,pyramid_mode)