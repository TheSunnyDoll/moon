    

from utils import *
from pybitget import Client
import argparse
import datetime

def earn_or_loss(huFu,x):
        startTime = get_previous_x_timestamp(x+2)
        endTime = get_previous_x_timestamp(x)
        # endTime = get_previous_minute_timestamp()
        orders = huFu.mix_get_history_orders(symbol, startTime, endTime, 100, lastEndId='', isPre=False)['data']['orderList']
        loss_list = []
        profit_list = []
        total_profits = 0
        total_loss = 0
        recent_open_long_list = []
        recent_open_short_list = []

        for order in orders:
            uTime = timestamp_to_time(float(order['uTime'])).strftime("%Y-%m-%d %H:%M:%S")
            week  = date_to_week(uTime)
            if float(order['totalProfits']) < 0:
                delta = abs(float(order['totalProfits']) / float(order['size']))
                entry = float(order['priceAvg']) - float(order['totalProfits']) / float(order['size']) 
                loss_list.append([uTime ,week,order['size'],order['side'],entry,order['priceAvg'],order['totalProfits'],delta])
                total_loss += order['totalProfits']
            if float(order['totalProfits']) > 0:
                delta = abs(float(order['totalProfits']) / float(order['size']))
                entry = float(order['priceAvg']) - float(order['totalProfits']) / float(order['size']) 
                profit_list.append([uTime,week,order['size'],order['side'],entry,order['priceAvg'],order['totalProfits'],delta])
                total_profits += order['totalProfits']
            if order['side'] == 'open_long' and order['state'] == 'filled':
                 recent_open_long_list.append([uTime,order['size'],order['side'],order['priceAvg']])
            if order['side'] == 'open_short' and order['state'] == 'filled':
                 recent_open_short_list.append([uTime,order['size'],order['side'],order['priceAvg']])
        for i in loss_list:
            print(i)
        
        print(total_loss)
        for i in profit_list:
            print(i)

        print(total_profits)

        # 使用列表推导式找到在时间范围内的数据
        # 将数据按日期分组
        # grouped_data = {}
        # for entry in loss_list:
        #     date_str = entry[0][:10]  # 提取日期字符串，如 '2023-07-24'
        #     if date_str not in grouped_data:
        #         grouped_data[date_str] = []
        #     grouped_data[date_str].append(entry)

        # # 定义时间段的开始和结束时间
        # start_time = datetime.datetime.strptime('06:00:00', '%H:%M:%S').time()
        # end_time = datetime.datetime.strptime('10:00:00', '%H:%M:%S').time()

        # # 找到每天在时间范围内的数据
        # filtered_data = []
        # for date_str, entries in grouped_data.items():
        #     for entry in entries:
        #         entry_time = datetime.datetime.strptime(entry[0][-8:], '%H:%M:%S').time()
        #         if start_time <= entry_time <= end_time:
        #             filtered_data.append(entry)
        # print(filtered_data)


if __name__ == "__main__":
    symbol = 'BTCUSDT_UMCBL'
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    args = parser.parse_args()

    heroname = args.username
    config = get_config_file()
    hero = config[heroname]
    huFu = Client(hero['api_key'], hero['secret_key'], hero['passphrase'])
    for i in range(10):
        earn_or_loss(huFu,i)


