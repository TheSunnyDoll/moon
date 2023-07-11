from pybitget import Client
import argparse
from utils import *


symbol = 'BTCUSDT_UMCBL'
marginCoin = 'USDT'
qty = 0.55
side = 'open_short'
entry = 30785
tp = 29700
sl = 31070


parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username')
parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')

args = parser.parse_args()
heroname = args.username
debug_mode = args.debug_mode

config = get_config_file()
hero = config[heroname]

huFu = Client(hero['api_key'],hero['secret_key'],hero['passphrase'])
huFu.mix_place_plan_order(symbol, marginCoin, qty , side, 'limit', entry, "market_price", executePrice=entry,presetTakeProfitPrice=tp, presetStopLossPrice=sl, reduceOnly=False)
data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
for data in data:
    print(data)



new_long_sl = 0
new_short_sl = 29801
data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
for plan in data:
    if plan['planType'] == 'loss_plan':
        if plan['side'] == 'close_long' and new_long_sl != 0:
            ## modifiy the sl
            try:
                size = plan['size']
                huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                huFu.mix_place_stop_order(symbol, marginCoin, new_long_sl, 'loss_plan', 'long',triggerType='fill_price', size=size, rangeRate=None)      
                print(f"士气正盛！前移败退点！北军 新败退点: {new_long_sl} ")

            except Exception as e:
                print(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_sl} ,{e}")
            
        elif plan['side'] == 'close_short' and new_short_sl != 0:
            if new_short_sl < float(plan['triggerPrice']):
                ## modifiy the sl
                try:
                    size = plan['size']
                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                    huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=size, rangeRate=None)                            
                    print(f"士气正盛！前移败退点！ 南军 新败退点:  {new_short_sl} ")

                except Exception as e:
                    print(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")

data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
for data in data:
    print(data)
