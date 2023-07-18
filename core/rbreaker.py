from pybitget import Client
import time
import copy
from utils import *
import argparse
from corps import *

## 动态止损   
#   long: delta = entry - sl , current_price >= entry + delta/2 , new_sl = current_price - delta , if new_sl > sl , sl = new_sl
##      一单有一单爆破盈利，则改动剩余仓位止损
## 假突破处理 ，
#    一个方向假突破致使5成以上soldier died，
#       died soldier 复活，血量翻倍，一个交易区间限定一次
#      另一个方向进入复仇模式，直接翻倍，限定一次

## 构建交易区间rb0 ， rb1 ，rb 2
## 交易方法一：
# 构建区间：17:00 - 02:59 不交易，
# 延伸区间：03:00 - 16:59 交易 ： 
#       基础设置（核心收益），突破线开单，突破线 - 中轴线 = 盈利点 - 突破线 ，盈亏 1:1

# 一个区间，即一天最多交易突破 4次 ，blsh 不限

# 区间分类：            适合兵种
#   小区间 
#   中区间
#   大区间
#   超大区间




class Rbreaker():
    def __init__(self) -> None:
        self.pivot = 0    # 枢轴点
        self.bBreak = 0 # 突破买入价
        self.sSetup = 0 # 观察卖出价
        self.sEnter = 0  # 反转卖出价
        self.bEnter = 0  # 反转买入价
        self.bSetup = 0 # 观察买入价
        self.sBreak = 0 # 突破卖出价
        self.type = ''

    ## TODO:update params
    ## range decide
    def today_range_decide(self,symbol,huFu,rest_time):
        today_range_kline = []
        today_range = []

        current_hour = get_current_hour()
        if  current_hour <= rest_time[0] or current_hour >= rest_time[1]:
            startTime = get_previous_day_timestamp()
            endTime = get_previous_hour_timestamp()

            ## OHLC 2,3
            data = huFu.mix_get_candles(symbol,'1H',startTime,endTime)
            data = data[-24:]

            for dt in data:
                hour = timestamp_to_hour(float(dt[0]))
                if rest_time[0] < hour <rest_time[1]:
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

    ## 判断并设定区间类型
    def set_range_type(self):
        pass


    def if_blsh(self,current_price):
        ## 判断是否在区间内
        bBreak = float(self.bBreak)
        sBreak = float(self.sBreak)
        sSetup = float(self.sSetup)
        bSetup = float(self.bSetup)
        bEnter = float(self.bEnter)
        sEnter = float(self.sEnter)
        if bBreak > current_price > sBreak:
            # 判断是否可以blsh, delta大于千分之一
            alpha = bBreak * 0.001
            delta = sSetup - bSetup
            if delta >= alpha:
                sc = get_current_second()
                if sc % 10 == 1:
                    logger.warning("边防来报～ 城内有奸细 🥷 潜入，请小心！！")
                return True
            else:
                return False
            
        return False
    
    def blsh(self,symbol,marginCoin,huFu,blsh_need_plan,current_price,base_qty):
        can_sell = False
        can_buy = False
        if self.bBreak > current_price > self.sEnter:
            logger.warning("北瞭望塔发现奸细移动，巡逻兵加强警备！！")
            can_sell =True
        elif self.bEnter > current_price > self.sBreak:
            logger.warning("南瞭望塔发现奸细移动，巡逻兵加强警备！！")
            can_buy = True
        ## condition
        # 1: sell at sEnter --- 
        for plan in blsh_need_plan:
            if plan == 'blsh_sell_to_pivot' and can_sell:
                #   tp at pivot, sl at bBreak , qty = 2x
                huFu.mix_place_plan_order(symbol, marginCoin, base_qty * 2, 'open_short', 'limit', self.sEnter, "market_price", executePrice=self.sEnter, clientOrderId='blsh_sell_to_pivot',presetTakeProfitPrice=self.pivot, presetStopLossPrice=self.bBreak, reduceOnly=False)
                logger.info("南军巡逻兵已出动, 代号 %s ,蹲守点 北宣武门 %s", 'blsh_sell_to_pivot',self.sEnter)            
            
            elif plan == 'blsh_sell_to_bEnter' and can_sell:
                #                       tp at bEnter , sl at bBreak ,qty = 1x
                huFu.mix_place_plan_order(symbol, marginCoin, base_qty , 'open_short', 'limit', self.sEnter, "market_price", executePrice=self.sEnter, clientOrderId='blsh_sell_to_bEnter',presetTakeProfitPrice=self.bEnter, presetStopLossPrice=self.bBreak, reduceOnly=False)
                logger.info("南军巡逻兵已出动, 代号 %s ,蹲守点 北宣武门 %s", 'blsh_sell_to_bEnter',self.sEnter)            

            elif plan == 'blsh_buy_to_pivot' and can_buy:
                # 2: buy  at bEnter --- tp at pivot, sl at sBreak , qty = 2x
                huFu.mix_place_plan_order(symbol, marginCoin, base_qty * 2, 'open_long', 'limit', self.bEnter, "market_price", executePrice=self.bEnter, clientOrderId='blsh_buy_to_pivot',presetTakeProfitPrice=self.pivot, presetStopLossPrice=self.sBreak, reduceOnly=False)
                logger.info("北军巡逻兵已出动, 代号 %s ,蹲守点 南宣武门 %s", 'blsh_buy_to_pivot',self.sEnter)            

            elif plan == 'blsh_buy_to_sEnter' and can_buy:
                #                       tp at sEnter , sl at sBreak  ,qty = 1x
                huFu.mix_place_plan_order(symbol, marginCoin, base_qty , 'open_long', 'limit', self.bEnter, "market_price", executePrice=self.bEnter, clientOrderId='blsh_buy_to_sEnter',presetTakeProfitPrice=self.sEnter, presetStopLossPrice=self.sBreak, reduceOnly=False)
                logger.info("北军巡逻兵已出动, 代号 %s ,蹲守点 南宣武门 %s", 'blsh_buy_to_sEnter',self.sEnter)            


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
    def arrange(self,soldier_qty,long_sl_end,short_sl_end,side,qty):

        # transform
        long_sl_end = float(long_sl_end)
        short_sl_end = float(short_sl_end)
        long_start = float(self.long_start)
        long_end = float(self.long_end)
        short_start = float(self.short_start)
        short_end =float(self.short_end)

        if side == 'long' or side == 'both':
        # long chains
            long_chains = []
            pieces = 4
            long_entry_range = (long_end - long_start) / 4
            long_entry_piece = round(long_entry_range / pieces)
            long_sl_piece = round(long_entry_piece/2)

            for i in range(soldier_qty):
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

            for i in range(soldier_qty):
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


## Chief
class Chief:
    def __init__(self,key,secret,pwd) -> None:
        self.key = key
        self.secret = secret
        self.pwd = pwd
        self.placed = False
        self.huFu = None

    def new_huFu(self):
        huFu = Client(self.key,self.secret,self.pwd)
        self.huFu = huFu
        return huFu
    
    def deploy(self,corps,symbol, marginCoin,debug_mode):
        ## place trigger orders
        for corp in corps:
            for sd in corp:
                logger.info(f"大军准备, 士兵 代号  :{sd.id} , 带兵数量 {sd.qty} , 进攻方向  {sd.side}, 蹲守地点  {sd.entry} ,进攻目标  {sd.tp} , 败退点  {sd.sl}")
                if not debug_mode:
                    self.huFu.mix_place_plan_order(symbol, marginCoin, sd.qty , sd.side, 'limit', sd.entry, "market_price", executePrice=sd.entry, clientOrderId=sd.id,presetTakeProfitPrice=sd.tp, presetStopLossPrice=sd.sl, reduceOnly=False)
        ## set placed
        self.placed = True

    def reborn_sd(self,fire):
        #data = fire.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', lo[0], "market_price", executePrice=lo[0], presetTakeProfitPrice=lo[1], presetStopLossPrice=lo[2], reduceOnly=False)
        pass

    ## 收兵   撤离，所有单子  如果有仓位，cp +/- 50 作为tp/sl
    def withdraw(self):
        withdraw_delta = 50
        huFu = self.huFu
        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
                ## clear all open orders
            huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

        new_long_sl = 0
        new_short_sl = 0
        result = huFu.mix_get_single_position(symbol,marginCoin)
        pos = result['data']
        for order in pos:
            if order['holdSide'] == 'long':
                current_price = float(order['marketPrice'])
                long_qty = float(order["total"])
                if long_qty > 0:
                    new_long_sl = round(current_price - withdraw_delta)
                    new_long_tp = round(current_price + withdraw_delta)


            elif order['holdSide'] == 'short':
                current_price = float(order['marketPrice'])
                short_qty = float(order["total"])
                if short_qty > 0:
                    new_short_sl = round(current_price + withdraw_delta)
                    new_short_tp = round(current_price - withdraw_delta)

        try:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

        for plan in data:
            if plan['planType'] == 'loss_plan':
                if plan['side'] == 'close_long' and new_long_sl != 0:
                    if new_long_sl > float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            huFu.mix_place_stop_order(symbol, marginCoin, new_long_sl, 'loss_plan', 'long',triggerType='fill_price', size=plan['size'], rangeRate=None)      
                            logger.warning(f"鸣金收兵！大军速速归营，在战士兵移动败退点！北军 新败退点: {new_long_sl} ")

                        except Exception as e:
                            logger.warning(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_sl} ,{e}")
                        
                elif plan['side'] == 'close_short' and new_short_sl != 0:
                    if new_short_sl < float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=plan['size'], rangeRate=None)                            
                            logger.warning(f"鸣金收兵！大军速速归营，在战士兵移动败退点！南军 新败退点: {new_short_sl} ")

                        except Exception as e:
                            logger.warning(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")




def run(symbol,marginCoin,hero,rest_time,times,debug_mode):

    blsh_max_qty = 0.15 * float(times)
    logger.info(times)
    logger.info("最大巡逻兵力为: %f",blsh_max_qty)
    fire_max_qty = 0.2
    side = 'both'
    revenge_mode = False
    long_target = 0
    short_target = 0
    queque_length = 4 
    
    ## soldiers = 4 * 3 
    soldier_qty = 12 
    ## construct fireman
    chief = Chief(hero['api_key'],hero['secret_key'],hero['passphrase'])

    huFu = chief.new_huFu()


    ## get r-breaker
    rb = Rbreaker()
    blsh_oids = ['blsh_buy_to_sEnter','blsh_buy_to_pivot','blsh_sell_to_bEnter','blsh_sell_to_pivot']
    sds_oids = ['long_melee_0','long_melee_1','long_melee_2','long_melee_3',
                'short_melee_0','short_melee_1','short_melee_2','short_melee_3'
                ,'long_expedition_0','long_expedition_1','long_expedition_2','long_expedition_3'
                ,'short_expedition_0','short_expedition_1','short_expedition_2','short_expedition_3']

    # dies soldiers can reborn once, and place in roborn_oids list
    roborn_oids = []

    today_range = rb.today_range_decide(symbol,huFu,rest_time)
    if today_range != []:
        rb.set_range(today_range)
    logger.info("\n \t\t\t\t 玄武门   :%s\n\t\t\t\t 北瞭望塔 :%s\n\t\t\t\t 北宣武门 :%s\n\t\t\t\t 中军位   :%s\n\t\t\t\t 南宣武门 :%s\n\t\t\t\t 南瞭望塔 :%s\n\t\t\t\t 朱雀门   :%s\n ",rb.bBreak,rb.sSetup,rb.sEnter,rb.pivot,rb.bEnter,rb.bSetup,rb.sBreak)
    # # construct chains : 
    # long  start is rb.bBreak  
    # short start is rb.sBreakS
    long_delta = rb.bBreak - rb.sEnter
    short_delta = rb.bEnter - rb.sBreak
    test_long_end = float(rb.bBreak) + long_delta
    test_short_end = float(rb.sBreak) - short_delta
    base_qty = 0.1 * float(times)
    logger.info("基础兵力为: %f",base_qty)

    chains = Chain(rb.bBreak,test_long_end,rb.sBreak,test_short_end)
    long_chains,short_chains = chains.arrange(soldier_qty,rb.sEnter,rb.bEnter,side,base_qty)

    logger.info("玄武门外士兵站位表 %s",long_chains)
    logger.info("朱雀门外士兵站位表 %s",short_chains)

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
        data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        if data != []:
                ## clear all open orders
            huFu.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')

    logger.warning("三")
    time.sleep(1)
    logger.warning("二")
    time.sleep(1)
    logger.warning("一")
    time.sleep(1)
    logger.warning("全军戒备！！！随时准备迎敌！！！")

    trade = True

    while trade:
        
        # reset the params
        new_long_sl = 0
        new_short_sl = 0

        current_hour = get_current_hour()
        if  not 2 <= current_hour <=17:
            logger.info("天色不早～鸣金收兵！！！ 叮！叮！叮！ ")
            chief.withdraw()
            chief.placed = False

            break

        ## get current position
        try:
            result = huFu.mix_get_single_position(symbol,marginCoin)
            pos = result['data']
            long_qty = float(pos[0]["total"])
            short_qty = float(pos[1]["total"])
            if long_qty > 0:
                sc = get_current_second()
                if sc % 10 == 1:
                    logger.info("北军鏖战中🔥～，出兵🪖 数量 %s ，目前北军已斩获 %s 敌军，正在斩获 %s ，加油啊 ，兄弟们！！！",long_qty, pos[0]['achievedProfits'],pos[0]['unrealizedPL'])
            if short_qty > 0:
                sc = get_current_second()
                if sc % 10 == 1:
                    logger.info("南军鏖战中🔥～，出兵🪖 数量 %s ，目前南军已斩获 %s 敌军，正在斩获 %s ，加油啊 ，兄弟们！！！",short_qty, pos[1]['achievedProfits'],pos[1]['unrealizedPL'])

            for order in pos:
                if order['holdSide'] == 'long':
                    long_pos = float(order['averageOpenPrice'])
                    current_price = float(order['marketPrice'])
                    if current_price >= long_pos + long_delta/2 :
                        new_long_sl = round(current_price - long_delta*0.6)
                elif order['holdSide'] == 'short':
                    short_pos = float(order['averageOpenPrice'])
                    current_price = float(order['marketPrice'])
                    if current_price <= short_pos - short_delta/2 :
                        new_short_sl = round(current_price + short_delta*0.6)



        # long : new_sl = current_price - delta , if new_sl > sl , sl = new_sl  
        # short: if cp <= short_pos - short_delta/2 , if new_sl < sl ,sl = new_sl
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_single_position(): {e}")

        try:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='profit_loss')['data']
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

        for plan in data:
            if plan['planType'] == 'loss_plan':
                if plan['side'] == 'close_long' and new_long_sl != 0:
                    if new_long_sl > float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            size = plan['size']
                            huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            huFu.mix_place_stop_order(symbol, marginCoin, new_long_sl, 'loss_plan', 'long',triggerType='fill_price', size=size, rangeRate=None)      
                            logger.warning(f"士气正盛！前移败退点！北军 新败退点: {new_long_sl} ")

                        except Exception as e:
                            logger.warning(f"move long sl faild, order id is {plan['orderId']},new_long_sl is {new_long_sl} ,{e}")
                        
                elif plan['side'] == 'close_short' and new_short_sl != 0:
                    if new_short_sl < float(plan['triggerPrice']):
                        ## modifiy the sl
                        try:
                            size = plan['size']
                            huFu.mix_cancel_plan_order(symbol, marginCoin, plan['orderId'], 'loss_plan')
                            huFu.mix_place_stop_order(symbol, marginCoin, new_short_sl, 'loss_plan', 'short',triggerType='fill_price', size=size, rangeRate=None)                            
                            logger.warning(f"士气正盛！前移败退点！ 南军 新败退点:  {new_short_sl} ")

                        except Exception as e:
                            logger.warning(f"move short sl faild, order id is {plan['orderId']},new_short_sl is {new_short_sl} ,{e}")


        ## get current price 
        try:
            result = huFu.mix_get_market_price(symbol)
            current_price = result['data']['markPrice']
            logger.info("斥候来报，坐标 %s 处发现敌军",current_price)
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_market_price(): {e}")

        # check current plan
        blsh_need_plan = copy.deepcopy(blsh_oids)
        sd_need_plan = copy.deepcopy(sds_oids)

        try:
            data = huFu.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        except Exception as e:
            logger.warning(f"An unknown error occurred in mix_get_plan_order_tpsl(): {e}")

        for plan in data:
            if plan['clientOid'] in blsh_need_plan:
                try:
                    blsh_need_plan.remove(plan['clientOid'])
                except Exception as e:
                    logger.warning(f"An unknown error occurred in cancel_entry(): {e}")
            if plan['clientOid'] in sds_oids:
                chief.placed = True

            
        ## if blsh
        if rb.if_blsh(float(current_price))  and long_qty < blsh_max_qty and short_qty < blsh_max_qty and blsh_need_plan != []:
            ## blsh
            if not debug_mode:
                rb.blsh(symbol,marginCoin,huFu,blsh_need_plan,float(current_price),base_qty)

        ## check if fireman placed
        if chief.placed == False and long_qty <= blsh_max_qty and short_qty <= blsh_max_qty:
            chief.deploy(corps,symbol, marginCoin,debug_mode)

        ## check corps soldiers
        ## if sodiers is died && not reborned , reborn


        ## check if update the range 
        ## if range updated,reset same params like roborned_list

        time.sleep(10)


if __name__ == '__main__':
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    logger.info("welcome to the rbreaker world!")
    logger.info("天色看来尚早 🌛～")
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-x', '--xtimes', default=1,help='x times base')

    args = parser.parse_args()
    heroname = args.username
    debug_mode = args.debug_mode
    times = args.xtimes

    config = get_config_file()
    hero = config[heroname]
    rest_time = [13,19]

# 13 - 19 rest
    while True:
        current_hour = get_current_hour()
        minute = get_current_minute()
        if  current_hour <= rest_time[0] or current_hour >= rest_time[1]:
            logger.info("起床！起床！ 军旅生涯新的一天开始啦！！！")
            run(symbol,marginCoin,hero,rest_time,times,debug_mode)
        if minute ==0:
            logger.info(f"这才 {current_hour} 点 , 继续睡吧,兄弟 ~~")
        time.sleep(10)

# 19 + 13 = 32 
# 19 - 32 