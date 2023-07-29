from risk_manager import *
from pybitget import Client
import time
import argparse
from utils import *

def start(hero,balance_rate,debug_mode):
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    rsm = Risk_manager(0,0,0,balance_rate)

    while True:
        try :
            dex = huFu.mix_get_accounts(productType='UMCBL')['data'][0]['usdtEquity']
            if rsm.balance_rate > 0:
                dex_spot = huFu.spot_get_account_assets(coin='USDT')['data'][0]['available']
                to_where,amount = rsm.rebalance(float(dex),float(dex_spot))
                print(dex_spot,to_where,amount)
                if to_where != '':
                    if not debug_mode:
                        if to_where == 'to_future':
                            huFu.spot_transfer('spot', 'mix_usdt', amount, 'USDT', clientOrderId=None)
                        elif to_where == 'to_spot':
                            print("hi")
                            huFu.spot_transfer('mix_usdt','spot', amount, 'USDT', clientOrderId=None)
                            print("low")

                    print("平衡获利: %s %f",to_where,amount)
        except Exception as e:
            print(f"An unknown error occurred in rebalance(): {e}")

        time.sleep(24*3600)



if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-br', '--balance_rate', default=0.5,help='balance_rate')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')

    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode

    balance_rate = float(args.balance_rate)


    config = get_config_file()
    hero = config[heroname]

    start(hero,balance_rate,debug_mode)