from pybitget import Client
import argparse
from utils import *



def calculate_position_size(max_loss_ratio, stop_loss_points, account_balance):
    risk_amount = account_balance * max_loss_ratio
    position_size = risk_amount / stop_loss_points
    return position_size



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
parser.add_argument('-o', '--order', action='store_true', default=False, help='Enable order mode')

parser.add_argument('-c', '--cancel', help='cancel order id ', default=0)
parser.add_argument('-m', '--move', action='store_true', default=False, help='Enable move sl mode')
parser.add_argument('-b', '--balance',  default=0 ,help='calculate position size by balance ')


args = parser.parse_args()
heroname = args.username
debug_mode = args.debug_mode
order = args.order
orderId = args.cancel
move = args.move
dex = args.balance

config = get_config_file()
hero = config[heroname]
huFu = Client(hero['api_key'],hero['secret_key'],hero['passphrase'])

if dex != 0:
    max_loss_ratio = 0.03  # 最大仓位亏损比例为2%
    stop_loss_points = 100  # 亏损点数为100

    position_size = calculate_position_size(max_loss_ratio, stop_loss_points, dex)
    print("应开仓位数：", position_size)


if order :
    huFu.mix_place_plan_order(symbol, marginCoin, qty , side, 'limit', entry, "market_price", executePrice=entry,presetTakeProfitPrice=tp, presetStopLossPrice=sl, reduceOnly=False)

if orderId != 0:
    huFu.mix_cancel_plan_order(symbol, marginCoin, orderId, 'normal_plan')

print("plan orders -------------------------")
data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
for data in data:
    print(data)
print("positions orders -------------------------")

result = huFu.mix_get_single_position(symbol,marginCoin)
pos = result['data']
for pos in pos:
    print(pos)

new_long_sl = 0
new_short_sl = 30800
new_short_tp = 29801
new_long_tp = 0

if move:
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
                ## modifiy the sl
                try:
                    size = plan['size']
                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                    huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=size, rangeRate=None)                            
                    print(f"士气正盛！前移败退点！ 南军 新败退点:  {new_short_sl} ")

                except Exception as e:
                    print(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")

        if plan['planType'] == 'profit_plan':
            if plan['side'] == 'close_long' and new_long_tp != 0:
                ## modifiy the sl
                try:
                    size = plan['size']
                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'profit_plan')
                    huFu.mix_place_stop_order(symbol, marginCoin, new_long_tp, 'profit_plan', 'long',triggerType='fill_price', size=size, rangeRate=None)      
                    print(f"士气正盛！前移止盈点！北军 新止盈点: {new_long_tp} ")

                except Exception as e:
                    print(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_tp} ,{e}")
                
            elif plan['side'] == 'close_short' and new_short_tp != 0:
                ## modifiy the sl
                try:
                    size = plan['size']
                    huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'profit_plan')
                    huFu.mix_place_stop_order(symbol, marginCoin, new_short_tp, 'profit_plan', 'short',triggerType='fill_price', size=size, rangeRate=None)                            
                    print(f"士气正盛！前移止盈点！ 南军 新止盈点:  {new_short_tp} ")

                except Exception as e:
                    print(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_tp} ,{e}")

print("tp orders -------------------------")

data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
for data in data:
    print(data)




