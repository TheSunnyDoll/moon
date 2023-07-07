from pybitget import Client
import time
import copy
from utils import *
import argparse


## 动态止损   
#   long: delta = entry - sl , current_price >= entry + delta/2 , new_sl = current_price - delta , if new_sl > sl , sl = new_sl
##      一单有一单爆破盈利，则改动剩余仓位止损
## 假突破处理 ，
#    一个方向假突破致使5成以上soldier died，
#       died soldier 复活，血量翻倍，一个交易区间限定一次
#      另一个方向进入复仇模式，直接翻倍，限定一次

## 下单时 设为： Flase
debug_mode = True


## 构建交易区间rb0 ， rb1 ，rb 2
## 交易方法一：
# 构建区间：17:00 - 02:59 不交易，
# 延伸区间：03:00 - 16:59 交易 ： 
#       基础设置（核心收益），突破线开单，突破线 - 中轴线 = 盈利点 - 突破线 ，盈亏 1:1

# 一个区间，即一天最多交易突破 4次 ，blsh 不限



class Rbreaker():
    def __init__(self) -> None:
        self.pivot = 0    # 枢轴点
        self.bBreak = 0 # 突破买入价
        self.sSetup = 0 # 观察卖出价
        self.sEnter = 0  # 反转卖出价
        self.bEnter = 0  # 反转买入价
        self.bSetup = 0 # 观察买入价
        self.sBreak = 0 # 突破卖出价

    ## TODO:update params
    ## range decide
    def today_range_decide(self,symbol,fire):
        today_range_kline = []
        today_range = []

        current_hour = get_current_hour()
        if  2 <= current_hour <=17:
            startTime = get_previous_day_timestamp()
            endTime = get_previous_hour_timestamp()

            ## OHLC 2,3
            data = fire.mix_get_candles(symbol,'1H',startTime,endTime)

            for dt in data:
                hour = timestamp_to_hour(float(dt[0]))
                if not 2 <= hour <=17:
                    today_range_kline.append(dt)

            ## rm the first element
            del(today_range_kline[0])
            highest = 0
            lowest = 100000

            for kline in today_range_kline:
                high = float(kline[2])
                if high > highest:
                    highest = high
                low = float(kline[3])
                if low < lowest:
                    lowest = low
            today_range.append(highest)
            today_range.append(lowest)
            print(f"today :{today_range}")
        return today_range

    def set_range(self,today_range):
        break_coef = 0.05
        setup_coef = 0.6
        enter_coef = 0.4

        high = today_range[0]
        low = today_range[1]
        pivot = round((high + low) / 2)  # 枢轴点
        delta = pivot - low
        bBreak = round(high + break_coef * delta)  # 突破买入价
        sSetup = round(pivot + setup_coef * delta)  # 观察卖出价
        sEnter = round(pivot + enter_coef * delta)  # 反转卖出价
        bEnter = round(pivot - enter_coef * delta)  # 反转买入价
        bSetup = round(pivot - setup_coef * delta)  # 观察买入价
        sBreak = round(low - break_coef * delta)  # 突破卖出价

        self.pivot = pivot
        self.bBreak = bBreak
        self.sSetup = sSetup
        self.sEnter = sEnter
        self.bEnter = bEnter
        self.bSetup = bSetup
        self.sBreak = sBreak

    ## 考虑是否随着假突破改变突破价格



    def if_blsh(self,current_price):
        ## 判断是否在区间内
        bBreak = float(self.bBreak)
        sBreak = float(self.sBreak)
        sSetup = float(self.sSetup)
        bSetup = float(self.bSetup)
        if bBreak > current_price > sBreak:
            # 判断是否可以blsh, delta大于千分之一
            alpha = bBreak * 0.001
            delta = sSetup - bSetup
            if delta >= alpha:
                print("true")
                return True
            else:
                return False
            
        print("false")

        return False
    
    def blsh(self,symbol,marginCoin,fire,blsh_need_plan,current_price,base_qty):
        print("start blsh")
        can_sell = False
        can_buy = False
        if self.bBreak > current_price > self.sEnter:
            can_sell =True
        elif self.bEnter > current_price > self.sBreak:
            can_buy = True
        ## condition
        # 1: sell at sEnter --- 
        for plan in blsh_need_plan:
            if plan == 'blsh_sell_to_pivot' and can_sell:
                #   tp at pivot, sl at bBreak , qty = 2x
                fire.mix_place_plan_order(symbol, marginCoin, base_qty * 2, 'open_short', 'limit', self.sEnter, "market_price", executePrice=self.sEnter, clientOrderId='blsh_sell_to_pivot',presetTakeProfitPrice=self.pivot, presetStopLossPrice=self.bBreak, reduceOnly=False)            
            elif plan == 'blsh_sell_to_bEnter' and can_sell:
                #                       tp at bEnter , sl at bBreak ,qty = 1x
                fire.mix_place_plan_order(symbol, marginCoin, base_qty , 'open_short', 'limit', self.sEnter, "market_price", executePrice=self.sEnter, clientOrderId='blsh_sell_to_bEnter',presetTakeProfitPrice=self.bEnter, presetStopLossPrice=self.bBreak, reduceOnly=False)
            elif plan == 'blsh_buy_to_pivot' and can_buy:
                # 2: buy  at bEnter --- tp at pivot, sl at sBreak , qty = 2x
                fire.mix_place_plan_order(symbol, marginCoin, base_qty * 2, 'open_long', 'limit', self.bEnter, "market_price", executePrice=self.bEnter, clientOrderId='blsh_buy_to_pivot',presetTakeProfitPrice=self.pivot, presetStopLossPrice=self.sBreak, reduceOnly=False)
            elif plan == 'blsh_buy_to_sEnter' and can_buy:
                #                       tp at sEnter , sl at sBreak  ,qty = 1x
                fire.mix_place_plan_order(symbol, marginCoin, base_qty , 'open_long', 'limit', self.bEnter, "market_price", executePrice=self.bEnter, clientOrderId='blsh_buy_to_sEnter',presetTakeProfitPrice=self.sEnter, presetStopLossPrice=self.sBreak, reduceOnly=False)


## chain
class Chain:
    def __init__(self,long_start,long_end,short_start,short_end) -> None:
        self.long_start = long_start
        self.long_end = long_end
        self.long_unit = 0
        self.long_unit_length = 0
        self.long_chains = []

        self.short_start = short_start
        self.short_end = short_end
        self.short_unit = 0
        self.short_unit_length = 0
        self.short_chains = []

    ## 细化成多单        
    # # 同一个entry 点 , 分单 entry + 万分之三 * i，发盈亏比1:1 - 1:3 
    def arrange(self,long_sl_end,short_sl_end,side,qty):

        # transform
        long_sl_end = float(long_sl_end)
        short_sl_end = float(short_sl_end)
        long_start = float(self.long_start)
        long_end = float(self.long_end)
        short_start = float(self.short_start)
        short_end =float(self.short_end)

        ## soldiers = 4 * 3 
        soldiers = 12 

        if side == 'long' or side == 'both':
        # long chains
            long_chains = []
            pieces = 4
            long_entry_range = (long_end - long_start) / 4
            long_entry_piece = round(long_entry_range / pieces)
            long_sl_piece = round(long_entry_piece/2)

            for i in range(soldiers):
                mul = i + 1
                step = round(long_entry_piece * mul)
                sl_step = long_sl_piece * mul
                if mul == 1 or (mul >=pieces and (mul % pieces == 1 or mul % pieces == 0) ):
                    size = qty
                else:
                    size = qty * 2
                order = [long_start + step , long_sl_end + sl_step, size]
                long_chains.append(order)

        if side == 'short' or side == 'both':
            # short chains
            short_chains = []
            pieces = 4
            short_entry_range = (short_start - short_end) / 4
            short_entry_piece = round(short_entry_range / pieces)
            short_sl_piece = round(short_entry_piece/2)

            for i in range(soldiers):
                mul = i + 1
                step = round(short_entry_piece * mul)
                sl_step = short_sl_piece * mul
                if mul == 1 or (mul >=pieces and (mul % pieces == 1 or mul % pieces == 0) ):
                    size = qty
                else:
                    size = qty * 2
                order = [short_start - step , short_sl_end - sl_step, size]
                short_chains.append(order)

        return long_chains,short_chains  

## soldier                 ## 血量               ## 步程        ## 活动范围             ##盈亏
## 巡逻兵——Patrolman：      0.1/0.2/0.2/0.1         1               内                  用盈利来决定亏损
# 近战兵——melee ：          0.1/0.2/0.2/0.1         1               外                  用亏损来决定盈利
# 远征兵——Expeditionary：   0.1/0.2/0.2/0.1         2               外                  用亏损来决定盈利
# 敢死队——Expendables：     0.05/0.1/0.05         爆破位             外                  用亏损来决定盈利
# 中军大帐——citadel

class Soldier:
    def __init__(self,side,entry,sl,qty) -> None:
        self.side = side
        self.entry = entry
        self.tp = 0
        self.sl = sl
        self.qty = qty 
        self.id = ''
        self.reborn = False

    def to_melee(self,base_qty):
        pace = 0.8
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = self.entry + delta
            elif self.qty == base_qty * 2:
                self.tp = self.entry + round(delta * pace)

        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = self.entry - delta
            elif self.qty == base_qty * 2:
                self.tp = self.entry - round(delta * pace)

    def to_expedition(self,base_qty):
        long_pace = 2
        short_pace = 1.5
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = self.entry + round(delta * long_pace)
            elif self.qty == base_qty * 2:
                self.tp = self.entry + round(delta * short_pace)
        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = self.entry - round(delta * long_pace)
            elif self.qty == base_qty * 2:
                self.tp = self.entry - round(delta * short_pace)

    def to_expendable(self,base_qty,long_target,short_target):
        base_qty = base_qty /2
        print(f"expendable's base qty is {base_qty}")
        short_pace = 2.5
        delta = abs(self.entry - self.sl)
        if self.side == 'open_long':
            if self.qty == base_qty:
                self.tp = long_target
            elif self.qty == base_qty * 2:
                self.tp = self.entry + delta * short_pace
        elif self.side == 'open_short':
            if self.qty == base_qty:
                self.tp = short_target
            elif self.qty == base_qty * 2:
                self.tp = self.entry - delta * short_pace
 

## corps
# 近战兵——melee ：          0.1/0.2/0.2/0.1         1               外
# 远征兵——Expeditionary：   0.1/0.2/0.2/0.1         2               外
# 敢死队——Expendables：     0.05/0.1/0.05         爆破位             外

class Corps:
    def __init__(self) -> None:
        pass
    
    def queque_melee(self,sds,base_qty):
        queque = []
        i = 0
        for sd in sds:
            sd.to_melee(base_qty)
            if sd.side == 'open_long':
                sd.id = 'long_melee_'+ str(i)
            elif sd.side == 'open_short':
                sd.id = 'short_melee_'+ str(i)
            queque.append(sd)
            i+=1
        return queque

    def queque_expedition(self,sds,base_qty):
        queque = []
        i = 0
        for sd in sds:
            sd.to_expedition(base_qty)
            if sd.side == 'open_long':
                sd.id = 'long_expedition_'+ str(i)
            elif sd.side == 'open_short':
                sd.id = 'short_expedition_'+ str(i)
            queque.append(sd)
            i+=1
        return queque



## Fireman
class Fireman:
    def __init__(self,key,secret,pwd) -> None:
        self.key = key
        self.secret = secret
        self.pwd = pwd
        self.placed = False

    def new_fire(self):
        fire = Client(self.key,self.secret,self.pwd)
        return fire
    
    def fire(self,fire,corps,symbol, marginCoin):
        ## place trigger orders
        for corp in corps:
            for sd in corp:
                print(f"sd id is :{sd.id} ,qty is {sd.qty} , side is {sd.side}, entry is {sd.entry} ,tp is {sd.tp} , sl is {sd.sl}")
                if not debug_mode:
                    fire.mix_place_plan_order(symbol, marginCoin, sd.qty , sd.side, 'limit', sd.entry, "market_price", executePrice=sd.entry, clientOrderId=sd.id,presetTakeProfitPrice=sd.tp, presetStopLossPrice=sd.sl, reduceOnly=False)
        ## set placed
        self.placed = True

    def reborn_sd(self,fire):
        #data = fire.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', lo[0], "market_price", executePrice=lo[0], presetTakeProfitPrice=lo[1], presetStopLossPrice=lo[2], reduceOnly=False)
        pass


def run(symbol,marginCoin,hero):

    blsh_max_qty = 0.15
    fire_max_qty = 0.2
    side = 'both'
    revenge_mode = False
    long_target = 0
    short_target = 0
    queque_length = 4 
    
    ## construct fireman
    fm = Fireman(hero['api_key'],hero['secret_key'],hero['passphrase'])

    fire = fm.new_fire()


    ## get r-breaker
    rb = Rbreaker()
    blsh_oids = ['blsh_buy_to_sEnter','blsh_buy_to_pivot','blsh_sell_to_bEnter','blsh_sell_to_pivot']
    sds_oids = ['long_melee_0','long_melee_1','long_melee_2','long_melee_3',
                'short_melee_0','short_melee_1','short_melee_2','short_melee_3'
                ,'long_expedition_0','long_expedition_1','long_expedition_2','long_expedition_3'
                ,'short_expedition_0','short_expedition_1','short_expedition_2','short_expedition_3']

    # dies soldiers can reborn once, and place in roborn_oids list
    roborn_oids = []

    today_range = rb.today_range_decide(symbol,fire)
    if today_range != []:
        rb.set_range(today_range)
    print(rb.pivot,rb.bBreak,rb.sSetup,rb.sEnter,rb.bEnter,rb.bSetup,rb.sBreak)
    # # construct chains : 
    # long  start is rb.bBreak  
    # short start is rb.sBreakS
    long_delta = rb.bBreak - rb.sEnter
    short_delta = rb.bEnter - rb.sBreak
    test_long_end = float(rb.bBreak) + long_delta
    test_short_end = float(rb.sBreak) - short_delta
    base_qty = 0.1

    chains = Chain(rb.bBreak,test_long_end,rb.sBreak,test_short_end)
    long_chains,short_chains = chains.arrange(rb.sEnter,rb.bEnter,side,base_qty)

    print(long_chains)
    print(short_chains)
    corps = []

    if long_chains != []:
        melee_long_chains = long_chains[0:queque_length]
        expedition_long_chains = long_chains[queque_length:queque_length*2]
        expendable_long_chains = long_chains[queque_length*2:queque_length*3]


        ## construct long_corps
        long_cop = Corps()
        ## melee_long_queque
        melee_long = []
        for order in melee_long_chains:
            melee_sd_long = Soldier('open_long',order[0],order[1],order[2])
            melee_long.append(melee_sd_long)

        long_melee_queque = long_cop.queque_melee(melee_long,base_qty)
        corps.append(long_melee_queque)

        ## long_expedition_queque
        expedition_long = []
        for order in expedition_long_chains:
            expedition_sd_long = Soldier('open_long',order[0],order[1],order[2])
            expedition_long.append(expedition_sd_long)

        long_expedition_queque = long_cop.queque_expedition(expedition_long,base_qty)
        corps.append(long_expedition_queque)




    if short_chains != []:
        melee_short_chains = short_chains[0:queque_length]
        expedition_short_chains = short_chains[queque_length:queque_length*2]
        expendable_short_chains = short_chains[queque_length*2:queque_length*3]

        ## construct short_corps
        short_corp = Corps()
        melee_short = []
        ## melee_short_queque
        for order in melee_short_chains:
            melee_sd_short = Soldier('open_short',order[0],order[1],order[2])
            melee_short.append(melee_sd_short)
        short_melee_queque = short_corp.queque_melee(melee_short,base_qty)
        corps.append(short_melee_queque)

        ## short_expedition_queque
        expedition_short = []
        for order in expedition_short_chains:
            expedition_sd_short = Soldier('open_short',order[0],order[1],order[2])
            expedition_short.append(expedition_sd_short)

        short_expedition_queque = short_corp.queque_expedition(expedition_short,base_qty)
        corps.append(short_expedition_queque)




    if not debug_mode:
        data = fire.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
                ## clear all open orders
            fire.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

    print("3s later start!")
    time.sleep(3)
    trade = True

    while trade:
        
        # reset the params
        new_long_sl = 0
        new_short_sl = 0

        current_hour = get_current_hour()
        if  not 2 <= current_hour <=17:
            print("time to sleep ~ ")
            break

        ## get current position
        try:
            result = fire.mix_get_single_position(symbol,marginCoin)
            pos = result['data']
            long_qty = float(pos[0]["total"])
            short_qty = float(pos[1]["total"])
            print(long_qty,short_qty)
            for order in pos:
                if order['holdSide'] == 'long':
                    long_pos = float(order['averageOpenPrice'])
                    current_price = float(order['marketPrice'])
                    if current_price >= long_pos + long_delta/2 :
                        new_long_sl = round(current_price - long_delta)
                elif order['holdSide'] == 'short':
                    short_pos = float(order['averageOpenPrice'])
                    current_price = float(order['marketPrice'])
                    if current_price <= short_pos - short_delta/2 :
                        new_short_sl = round(current_price + short_delta)



        # long : new_sl = current_price - delta , if new_sl > sl , sl = new_sl  
        # short: if cp <= short_pos - short_delta/2 , if new_sl < sl ,sl = new_sl
        except Exception as e:
            print(f"An unknown error occurred in mix_get_single_position(): {e}")


        try:
            data = fire.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
        except Exception as e:
            print(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

        for plan in data:
            if plan['planType'] == 'loss_plan':
                if plan['side'] == 'close_long' and new_long_sl != 0:
                    if new_long_sl > float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            fire.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            fire.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'long',triggerType='fill_price', size=plan['size'], rangeRate=None)      
                            print(f"move long sl ,new_long_sl is {new_long_sl} ")

                        except Exception as e:
                            print(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_sl} ,{e}")
                        
                elif plan['side'] == 'close_short' and new_short_sl != 0:
                    if new_short_sl < float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            fire.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            fire.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=plan['size'], rangeRate=None)                            
                            print(f"move short sl ,new_short_sl is {new_short_sl} ")

                        except Exception as e:
                            print(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")


        ## get current price 
        try:
            result = fire.mix_get_market_price(symbol)
            current_price = result['data']['markPrice']
            print(current_price)
        except Exception as e:
            print(f"An unknown error occurred in mix_get_market_price(): {e}")

        # check current plan
        blsh_need_plan = copy.deepcopy(blsh_oids)
        sd_need_plan = copy.deepcopy(sds_oids)

        try:
            data = fire.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        except Exception as e:
            print(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

        for plan in data:
            if plan['clientOid'] in blsh_need_plan:
                try:
                    blsh_need_plan.remove(plan['clientOid'])
                except Exception as e:
                    print(f"An unknown error occurred in cancel_entry(): {e}")
            if plan['clientOid'] in sds_oids:
                fm.placed = True

            
        ## if blsh
        if rb.if_blsh(float(current_price))  and long_qty < blsh_max_qty and short_qty < blsh_max_qty and blsh_need_plan != []:
            ## blsh
            if not debug_mode:
                rb.blsh(symbol,marginCoin,fire,blsh_need_plan,float(current_price),base_qty)

        ## check if fireman placed
        if fm.placed == False and long_qty <= blsh_max_qty and short_qty <= blsh_max_qty:
            fm.fire(fire,corps,symbol, marginCoin)

        ## check corps soldiers
        ## if sodiers is died && not reborned , reborn


        ## check if update the range 
        ## if range updated,reset same params like roborned_list

        time.sleep(10)


if __name__ == '__main__':
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    print("welcome to the rbreaker world!")
    print("resting~~")
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    args = parser.parse_args()
    heroname = args.username

    config = get_config_file()
    hero = config[heroname]

    while True:
        current_hour = get_current_hour()
        minute = get_current_minute()
        if  2 <= current_hour <=17:
            print("time to work! man! ")
            run(symbol,marginCoin,hero)
        if minute ==0:
            print(f"it's just {current_hour} clock , keep resting,bro~~")
        time.sleep(10)
