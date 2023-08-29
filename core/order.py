from pybitget import Client
import argparse
from utils import *



def calculate_position_size(max_loss_ratio, stop_loss_points, account_balance):
    risk_amount = account_balance * max_loss_ratio
    position_size = risk_amount / stop_loss_points
    return position_size



symbol = 'BTCUSDT_UMCBL'
marginCoin = 'USDT'


parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username')
parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
parser.add_argument('-o', '--order', action='store_true', default=False, help='Enable order mode')

parser.add_argument('-c', '--cancel', help='cancel order id ', default=0)
parser.add_argument('-s', '--symbol', help='set symbol ', default='BTC')

parser.add_argument('-m', '--move', action='store_true', default=False, help='Enable move sl mode')
parser.add_argument('-b', '--balance',  default=0 ,help='calculate position size by balance ')

parser.add_argument('-cl', '--close', action='store_true', default=False, help='Enable close position mode')
parser.add_argument('-ca', '--cancelAll', action='store_true', default=False, help='cancel all')


args = parser.parse_args()
heroname = args.username
debug_mode = args.debug_mode
order = args.order
orderId = args.cancel
move = args.move
dex = args.balance
close = args.close
cancelAll = args.cancelAll
symbol = args.symbol


symbol = symbol +'USDT_UMCBL'


config = get_config_file()
hero = config[heroname]
huFu = Client(hero['api_key'],hero['secret_key'],hero['passphrase'])

if dex != 0:
    max_loss_ratio = 0.03  # 最大仓位亏损比例为2%
    stop_loss_points = 100  # 亏损点数为100

    position_size = calculate_position_size(max_loss_ratio, stop_loss_points, dex)
    print("应开仓位数：", position_size)

if cancelAll:
    try:
        data = huFu.mix_get_open_order('BTCUSDT_UMCBL')['data']
        if data != []:
            huFu.mix_cancel_all_orders ('UMCBL', marginCoin)
    except Exception as e:
        print(f"An unknown error occurred in mix_cancel_all_orders(): {e}")
    

    print("cancel all plan")
    # cancel all orders
    try:
        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
            for order in data:
                if order['planType'] == 'normal_plan':
                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'normal_plan')
                elif order['planType'] == 'track_plan':
                    huFu.mix_cancel_plan_order(symbol, marginCoin, order['orderId'],'track_plan')

            # huFu.mix_cancel_all_trigger_orders('UMCBL', 'track_plan')
            # huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

    except Exception as e:
        print(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

if order :
    qty = 1
    #side = 'open_long'
    side = 'open_short'

    entry = 30060
    tp = 29400
    sl = 30201

    huFu.mix_place_order(symbol,'USDT',qty,side,'limit',price=entry,reduceOnly=False, presetTakeProfitPrice=tp, presetStopLossPrice=sl)

if orderId != 0:
    huFu.mix_cancel_plan_order(symbol, marginCoin, orderId, 'normal_plan')

print("plan orders -------------------------")
data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
for data in data:
    print(data)
print("positions orders -------------------------")

result = huFu.mix_get_single_position(symbol,marginCoin)
position = result['data']
for pos in position:
    print(pos)


print("close orders qty -------------------------")

if close:
    long_qty = float(position[0]['total'])
    short_qty = float(position[1]['total'])

    print(long_qty)
    print(short_qty)
    if long_qty != '':
        data = huFu.mix_place_order(symbol,'USDT',long_qty,'close_long','market',reduceOnly=True)

    # if short_qty != '':
    #     data = huFu.mix_place_order(symbol,'USDT',short_qty,'close_short','market',reduceOnly=True)


new_short_sl = 26550
new_short_tp = 26280

new_long_sl = 0
new_long_tp = 0

if move:
    data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
    if data == [] and new_short_sl != 0:
        huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=pos['total'], rangeRate=None) 
        print(f"南军 新败退点: {new_short_sl} ")

    if data == [] and new_short_tp != 0:
        huFu.mix_place_stop_order(symbol, marginCoin, new_short_tp, 'profit_plan', 'short',triggerType='fill_price', size=pos['total'], rangeRate=None) 
        print(f"南军 新止盈点: {new_short_tp} ")

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




