# base on https://docs.thekingfisher.io/
from pybitget import Client

class Liquidation:
    def __init__(self) -> None:
        pass

    def get_liquidations(self,symbol):
        pass

    def select_best_postion(self,liquidations):
        pass


## chain

### range : 
# long : abs(start / end)
# short : start / end 

## step:
### 0.划：
#       （1）顺爆为突破交易：划定震荡区间，首单放置在区间外围外一点
#       （2）顺爆完成即为假突破交易，置突破完成后抄底

### 1.积：等多空爆仓比出现明显大差距
### 2.选：选择合适排列，选择合适手数
###     （1）多空比1:1，  2倍杠杆
###     （2）多空比2:1，  4倍杠杆
###     （3）多空比3:1，  6倍杠杆
###     （4）多空比4:1，  8倍杠杆
### 3.排：根据排列排单


class FireChain:
    def __init__(self,long_start,long_end,short_start,short_end) -> None:
        self.pct_range = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

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

    def get_chains(self):

        if self.long_start is not None and self.long_end is not None: # long
            start = self.long_start
            end = self.long_end
            pct_base = self.long_unit
            length = abs(start - end)
            p_base = max(abs(start),abs(end))
            c_base = round(p_base * pct_base)
            self.long_unit_length = c_base
            print(f"pct_base is : {pct_base} , base_length is {c_base}")
            c_times = round(length/c_base)
            print(f"opearate times : {c_times -1}")

            chains = []
            chains.append(start)
            for i in range(c_times):
                c_target_end = start + (i+1)*c_base
                chains.append(c_target_end)
            self.long_chains = chains
            
        if self.short_start is not None and self.short_end is not None: # short
            start = self.short_start
            end = self.short_end
            pct_base = self.short_unit
            length = abs(start - end)
            p_base = max(abs(start),abs(end))
            c_base = round(p_base * pct_base)
            self.short_unit_length = c_base
            print(f"pct_base is : {pct_base} , base_length is {c_base}")
            c_times = round(length/c_base)
            print(f"opearate times : {c_times -1}")

            chains = []
            chains.append(start)
            for i in range(c_times):
                c_target_end = start - (i+1)*c_base
                chains.append(c_target_end)
            print("let us make short orders !!")
            self.short_chains = chains
            

    def list_orders(self,pct_base,chains,dirc):
        pct_base = pct_base * 10000
        orders = []
        mul = 1.382
        order_times = len(chains)
        if dirc == 'long':
            dist = round(self.long_unit_length * mul)
            for i in range(order_times -2):
                base = chains[i+1]
                order = [base,base + dist,base - dist]
                orders.append(order)
                a = i+1
                exp_tp_pct = round((pct_base*(a-1)-3*(a+1))/10000,5)
                print(exp_tp_pct)
                exp_tp = exp_tp_pct * abs(chains[-1])
                print(f"the {i+1} order is : {order} , expect profit is {exp_tp}")
        if dirc == 'short':
            dist = round(self.short_unit_length * mul)
            for i in range(order_times -2):
                base = chains[i+1]
                order = [base,base - dist,base + dist]
                orders.append(order)
                a = i+1
                exp_tp_pct = round((pct_base*(a-1)-3*(a+1))/10000,5)
                print(exp_tp_pct)
                exp_tp = exp_tp_pct * abs(chains[-1])
                print(f"the {i+1} order is : {order} , expect profit is {exp_tp}")
        return orders


    def select_best_c_pct(self,start,end):
        start = start
        end = end
        length = abs(start - end)
        total_pct = round(length / start,5)
        print(f"total profit pct is {total_pct}")
        p_base = max(abs(start),abs(end))
        best_exp_pct = 0 
        best_exp_tp = 0

        for i in self.pct_range:
            i = round(i/10000,4)
            c_base = round(p_base * i)
            #print(f"pct_base is : {i} , base_length is {c_base}")
            c_times = round(length/c_base)
            op_times = c_times -1 
            #print(f"opearate times : {op_times}")
            exp_tp_pct = round((i*10000*(op_times-1)-3*(op_times+1))/10000,5)
            exp_tp = exp_tp_pct * abs(p_base)
            #print(f"expect profit pct is {exp_tp_pct} , profit is {exp_tp}")
            if exp_tp > best_exp_tp:
                best_exp_tp = exp_tp
                best_exp_pct = i
        expect_loss = (best_exp_pct + 0.0003) * abs(p_base)
        max_loss = expect_loss * op_times
        print(f"best profit is {best_exp_tp},best pct is {best_exp_pct} , expectloss is {expect_loss} , max loss is {max_loss}" )
        if start == self.long_start:
            self.long_unit = best_exp_pct
        elif start == self.short_start:
            self.short_unit = best_exp_pct

    ## inner chain ; strength chain
    ### 


    def select_best_multi(self,dex):
        long_length = self.long_chains[-1] - self.long_chains[0]
        short_length = self.short_chains[0] - self.short_chains[-1]
        base_qty = round(dex/self.short_chains[0],1)
        pct = round(long_length/short_length,2)
        if pct <=0.25 or pct >=4:
            mul = 8
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=0.33 or pct >= 3:
            mul = 6
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=0.5 or pct >= 2:
            mul = 4
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir
        
        elif pct <=1 or pct >= 1:
            mul = 2
            qty = base_qty*mul
            if pct >1:
                dir = 'long'
            else:
                dir = 'short'
            return mul,qty,dir

    # place 
    def place_orders(self,fire_man,symbol,marginCoin,qty,dir,long_orders,short_orders):
        # get current plan
        data = fire_man.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        for plan in data:
            print(plan)
        if data != []:
            ## clear all open orders
            fire_man.mix_cancel_all_trigger_orders('UMCBL', 'normal_plan')
            

        if dir == 'long':
            side = 'open_long'
            for lo in long_orders:
                ## order the trigger order 
                data = fire_man.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', lo[0], "market_price", executePrice=lo[0], presetTakeProfitPrice=lo[1], presetStopLossPrice=lo[2], reduceOnly=False)
                print(f"place long order at {lo[0]},tp at {lo[1]} , sl at {lo[2]}")
            
        elif dir == 'short':
            side = 'open_short'
            for so in short_orders:
                data = fire_man.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', so[0], "market_price", executePrice=so[0], presetTakeProfitPrice=so[1], presetStopLossPrice=so[2], reduceOnly=False)
                print(f"place short order at {so[0]},tp at {so[1]} , sl at {so[2]}")
        elif dir == 'both':
            side = 'open_long'
            for lo in long_orders:
                ## order the trigger order 
                data = fire_man.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', lo[0], "market_price", executePrice=lo[0], presetTakeProfitPrice=lo[1], presetStopLossPrice=lo[2], reduceOnly=False)
                print(f"place long order at {lo[0]},tp at {lo[1]} , sl at {lo[2]}")
            side = 'open_short'
            for so in short_orders:
                data = fire_man.mix_place_plan_order(symbol, marginCoin, qty, side, 'limit', so[0], "market_price", executePrice=so[0], presetTakeProfitPrice=so[1], presetStopLossPrice=so[2], reduceOnly=False)
                print(f"place short order at {so[0]},tp at {so[1]} , sl at {so[2]}")

        # check current plan
        data = fire_man.mix_get_plan_order_tpsl(symbol=symbol,isPlan='plan')['data']
        for plan in data:
            print(plan)

    def get_fire_man(self,api,secret,pwd):
        fire_man = Client(api,secret,pwd)

        ## try to get balance
        future = fire_man.mix_get_accounts(productType='UMCBL')
        dex = float(future['data'][0]['usdtEquity'])
        print(dex)
        mul,qty,dir = btc_fc.select_best_multi(dex)
        print(f"dex is {dex} , mul is {mul},qty is {qty},perfer {dir}")
        return fire_man,qty,dir



if __name__ == '__main__':

    btc_fc = FireChain(31050,31300,30960,30600)

    btc_fc.select_best_c_pct(btc_fc.long_start,btc_fc.long_end)
    btc_fc.select_best_c_pct(btc_fc.short_start,btc_fc.short_end)

    btc_fc.get_chains()
    
    print(f"long chain is {btc_fc.long_chains}")
    print("let us make long orders !!")
    long_orders = btc_fc.list_orders(btc_fc.long_unit,btc_fc.long_chains,'long')

    print(f"short chain is {btc_fc.short_chains}")
    print("let us make short orders !!")
    short_orders = btc_fc.list_orders(btc_fc.short_unit,btc_fc.short_chains,'short')

    ## start order
    symbol = 'BTCUSDT_UMCBL'
    marginCoin = 'USDT'
    #fire_man,qty,dir = btc_fc.get_fire_man("bg_2f2c7bcad16db7eaac00c52f162f5fe8","028bc30d5792376166d3c8e70c908bb188b06b4145acbba84911e767c3847814","aishuo999")
    fire_man,qty,diri = btc_fc.get_fire_man("bg_109f7cc0803eeb770c5e6ee7a84d5062","544bb76132737fc4b7b3b584ce705b74f6ed6a702f6635ccb37d0e22fe011a5c","aishuo999")
    #fire_man,qty,diri = btc_fc.get_fire_man("bg_e09bd29650e5c3cf517017566ddc8857","747467fe4ab031f3c92391c8d052f35c01d4fe8ea428bee2200da676456c1b98","Zz123456")

    dir = 'both'
    btc_fc.place_orders(fire_man,symbol,marginCoin,qty,dir,long_orders,short_orders)
