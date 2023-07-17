
from utils import *
from pybitget import Client
import argparse

# 结构交易： 机构需求> 宏观需求 > 短期流动性需求
# crypto ：临期期权商的价格需求 > 宏观价格需求 > 短期流动性价格需求
# 临期期权商的价格需求：每周五，NY开盘后（22点后——UTC+8）
# 重点：越临近月末的周五，期权商对价格需求越强烈，波动目的性越强

# top1 : 周五的option max pain （一周目标点）
# 周四/周五做po3，目标max pain 
# setup：（1h --- 15m --- 5m）
#   1.早晨查询 https://metrics.deribit.com/options/BTC ，寻找max_pain 并标记，利用max_pain 确定 options_bias
#   2.查询macro :    预估macro_bias （起效时间很短，推波助澜或者反options_bias，反时可以利用反来entry）
#   3.确定DR ——> 确定OTE,OTE区寻找pdArray (IFC > OB > FVG)，标记entry point
#   4.寻找consolidation，确定bsl / ssl ,预期judas
#   5.寻找tp/sl, 以sl 确定开仓数

# profile：
#   1.周三/周四 已经完成 accumulation  （1 legs + in sell model）

# intraday (expection):
#   1.开盘后consolidation （distribution）--->ASIA open , judas 进入 OTE 后 ---> 继续沿着 options_bias 快速移动 进入下一个 s/r 
#   2.在s/r 附近 consolidate (distribution) ---> NY open , judas ---> LD open , start to options_bias

class Po3():
    def __init__(self,symbol) -> None:
        self.symbol = symbol

    def get_max_pain(self):
        pass

    def get_options_bias(self,huFu,max_pain):
        # cp = get current price , bull if cp < max_pain else bear
        try:
            result = huFu.mix_get_market_price(symbol)
            current_price = result['data']['markPrice']
            logger.info("当前价格 %s ",current_price)
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_market_price(): {e}")

        if current_price < max_pain:
            return 'bull'
        else:
            return 'bear'

    def get_macro_bias():
        # get macro impact event, pre_data
        pass

    def get_OTE(self,options_bias,deal_range):
        ote = []
        # get dr_off = H-L 
        dr_off = deal_range[0] - deal_range[1]
        # if bear , OTE_H = L + (0.79 * dr_off) , OTE_L = L + (0.62 * dr_off)
        if options_bias == 'bear':
            ote_h = deal_range[1] + (0.79 * dr_off)
            ote_l = deal_range[1] + (0.62 * dr_off)
            ote.append(ote_h)
            ote.append(ote_l)
            return ote
        # if bull , OTE_H = H - (0.62 * dr_off) , OTE_L = H - (0.79 * dr_off)
        elif options_bias == 'bull':
            ote_h = deal_range[0] - (0.62 * dr_off)
            ote_l = deal_range[0] - (0.79 * dr_off)
            ote.append(ote_h)
            ote.append(ote_l)
            return ote        

    def get_pds(self,huFu):
        # lft - 5m -15m

        # get_fvg , get_ob , get_ifc ,get_bpr

        
        pass

    def get_entry(self,pds,OTE):
        entrys = []
        # for signal in pds , entry = signal if signal in OTE
        for signal in pds:
            if OTE[1] <= signal <= OTE[0]:
                entrys.append(signal)

        return entrys
    
    def get_sl_point(self,entrys,options_bias,deal_range):
        # slp = H - signal if bear else slp = signal - L
        slps = []
        for signal in entrys:
            if options_bias == 'bear':
                slp = deal_range[0] - signal
                pair = [signal,slp]
                slps.append(pair)
            elif options_bias == 'bull':
                slp = signal - deal_range[1]
                pair = [signal,slp]
                slps.append(pair)
        return slps

    def calculate_position_size(max_loss_ratio, stop_loss_points, account_balance):

        risk_amount = account_balance * max_loss_ratio
        position_size = risk_amount / stop_loss_points
        return position_size


    def get_deal_range(self,huFu,fight_time):
        today_range_kline = []
        today_range = []

        current_hour = get_current_hour()
        if  fight_time[0] <= current_hour <=fight_time[1]:
            startTime = get_previous_day_timestamp()
            endTime = get_previous_hour_timestamp()

            ## OHLC 2,3
            data = huFu.mix_get_candles(symbol,'1H',startTime,endTime)
            data = data[-24:]

            for dt in data:
                hour = timestamp_to_hour(float(dt[0]))
                if not fight_time[0] < hour <fight_time[1]:
                    today_range_kline.append(dt)

            ## rm the first element
            del(today_range_kline[0])
            highest = 0
            lowest = 100000

            if today_range_kline !=[]:
                for kline in today_range_kline:
                    high = float(kline[2])
                    if high > highest:
                        highest = high
                    low = float(kline[3])
                    if low < lowest:
                        lowest = low
                today_range.append(highest)
                today_range.append(lowest)
                logger.warning("今日守军范围⛺️ %s :",today_range)
            else:
                logger.warning("今日守军范围获取失败，请重新检查🧐")
        return today_range

def run(hero,symbol,range_time):
    huFu = Client(hero['api_key'],hero['secret_key'],hero['passphrase'])
    orders = []
    po3 = Po3(symbol)
    max_pain = po3.get_max_pain()
    options_bias = po3.get_options_bias(huFu,max_pain)
    macro_bias = po3.get_macro_bias()
    deal_range = po3.get_deal_range(huFu,range_time)
    dr,ote = po3.get_OTE(options_bias,deal_range)
    pds = po3.get_pds(huFu)
    entrys = po3.get_entry(pds,ote)
    sl_point = po3.get_sl_point(entrys,options_bias,dr)
    # get balance
    dex = 8000
    loss_ratio = 0.02
    for pair in sl_point:
        size = po3.calculate_position_size(loss_ratio,pair[1],dex)
        order = [pair[0],pair[1],max_pain,size]
        orders.append(order)

    # place orders

    for order in orders:
        # 
        pass


if __name__ == '__main__':
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    args = parser.parse_args()
    heroname = args.username
    config = get_config_file()
    hero = config[heroname]
    range_time = []
    run(hero,symbol,range_time)
