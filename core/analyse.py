    

from utils import *
from pybitget import Client
import argparse
import datetime
import pandas as pd

def earn_or_loss(huFu,x):
        print(x)
        if x == 0:
            startTime = get_previous_x_timestamp(x+1)

            endTime = get_previous_minute_timestamp()
        else:
            startTime = get_previous_x_timestamp(x+1)

            endTime = get_previous_x_timestamp(x)
        #endTime = get_previous_minute_timestamp()
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
                loss_list.append([uTime ,entry,week,order['size'],order['side'],order['priceAvg'],order['totalProfits'],delta])
                total_loss += order['totalProfits']
            if float(order['totalProfits']) > 0:
                delta = abs(float(order['totalProfits']) / float(order['size']))
                entry = float(order['priceAvg']) - float(order['totalProfits']) / float(order['size']) 
                profit_list.append([uTime,entry,week,order['size'],order['side'],order['priceAvg'],order['totalProfits'],delta])
                total_profits += order['totalProfits']
            if order['side'] == 'open_long' and order['state'] == 'filled':
                 recent_open_long_list.append([uTime,order['size'],order['side'],order['priceAvg']])
            if order['side'] == 'open_short' and order['state'] == 'filled':
                 recent_open_short_list.append([uTime,order['size'],order['side'],order['priceAvg']])

        columns = ['time', 'entry', 'week_day', 'qty', 'action', 'exit', 'T/L', 'points']
        week_days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        loss_df = pd.DataFrame(loss_list, columns=columns)
        profit_df = pd.DataFrame(profit_list, columns=columns)

        for day in week_days:
            loss_day_df = loss_df[loss_df['week_day'].str.contains(day)]
            profit_day_df = profit_df[profit_df['week_day'].str.contains(day)]
            if not loss_day_df.empty:
                # print(loss_day_df)
                print(loss_day_df['time'].iloc[0],day," Total loss sum:", loss_day_df['T/L'].sum())
            if not profit_day_df.empty:
                # print(profit_day_df)
                print(profit_day_df['time'].iloc[0],day," Total profit sum:", profit_day_df['T/L'].sum())
            if not loss_day_df.empty or not profit_day_df.empty:
                net_profit = loss_day_df['T/L'].sum() + profit_day_df['T/L'].sum()
                # print(day," net profit sum:", net_profit)
                if net_profit > 0:
                    pos = 1
                else:
                    pos = 0
            if loss_day_df['T/L'].sum() < 0:
                return loss_day_df['time'].iloc[0],day,profit_day_df['T/L'].sum(),loss_day_df['T/L'].sum(),net_profit,pos,profit_day_df['T/L'].max(),loss_day_df['T/L'].min()
            elif profit_day_df['T/L'].sum()>0:
                return profit_day_df['time'].iloc[0],day,profit_day_df['T/L'].sum(),loss_day_df['T/L'].sum(),net_profit,pos,profit_day_df['T/L'].max(),loss_day_df['T/L'].min()



        # count = loss_price_count(loss_list)
        # print(count)

        # renct = extract_recent_data(loss_list)
        # print("rec",renct)
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
    tl_list = []
    for i in range(10):
        date, week_day, profit ,loss, net ,pos,max_pro,max_dd= earn_or_loss(huFu,i)
        tl_list.append([date, week_day, profit ,loss, net,pos,max_pro,max_dd])

    columns = ['time', 'week_day', 'profit' ,'loss', 'net','pos','max_profit','max_loss']
    tl_list_pd = pd.DataFrame(tl_list, columns=columns)
    print(tl_list_pd)
    print(tl_list_pd['net'].sum())

    