from pybitget import Client
import argparse
from utils import *


symbol = 'BTCUSDT_UMCBL'
marginCoin = 'USDT'
qty = 0.55
side = 'open_short'
entry = 30620
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
