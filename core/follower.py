from exchange.bitget import Bitget
import time

## follow leader orders 

class Leader(Bitget):
    def __init__(self,key,secret,passphrase) -> None:
        super().__init__("bitget",key,secret,passphrase=passphrase)

    def get_open_orders(self,symbol):
        result = self.get_open_orders_bitget(symbol)
        infos = []
        for data in result:
            info = [data['price'],data['qty'],data['side'],data['reduce_only']]
            infos.append(info)      
        return infos


class Follower(Bitget):
    def __init__(self,key,secret,passphrase) -> None:
        super().__init__("bitget",key,secret,passphrase=passphrase)

    def get_open_orders(self,symbol):
        result = self.get_open_orders_bitget(symbol)
        infos = []
        for data in result:
            info = [data['price'],data['qty'],data['side'],data['reduce_only']]
            infos.append(info)      
        return infos
    
    def get_pct_orders(self,pct,ld_infos):
        fl_orders = []
        for info in ld_infos:
            order = info
            order[1] = round(float(info[1]) * pct , 3)
            fl_orders.append(order)
        return fl_orders

    def check_order_exist(self,pct_orders,fl_orders):
        cancel_orders = []
        exec_orders = pct_orders
        for fd in fl_orders:
            for po in pct_orders:
                if fd == po:
                    exec_orders.remove(fd)
                if po not in fl_orders:
                    cancel_orders.append(po)    
        return cancel_orders,exec_orders

    def copy_trade(self,symbol,exec_orders):
        for exo in exec_orders:
            # order = self.create_order(symbol, 'limit', exo[2], exo[1], exo[0], reduce_only=exo[3])
            print(f"place order : {exo}")
            # print(order)

    def check_long_position(self,ld_positions,fl_positions):
        pct_long_qty = round(float(ld_positions['long']['qty']) * pct , 3)
        fl_long_qty = round(float(fl_positions['long']['qty']) , 3)

        if pct_long_qty == fl_long_qty:
            return 0
        else:
            return abs(pct_long_qty - fl_long_qty)
        

    def check_short_position(self,ld_positions,fl_positions):
        pct_short_qty = round(float(ld_positions['short']['qty']) * pct , 3)
        fl_short_qty = round(float(fl_positions['short']['qty']) , 3)

        if pct_short_qty == fl_short_qty:
            return 0
        else:
            return abs(pct_short_qty - fl_short_qty)
        
    def cut_qty(self,diff_long,diff_short):
        if diff_long != 0:
            print(f"diff long is :{diff_long}")
            # self.create_order(symbol,'market','close_long',diff_long,reduce_only=True)
        elif diff_short != 0:
            print(f"diff short is :{diff_short}")
            # self.create_order(symbol,'market','close_short',diff_short,reduce_only=True)

    def cancel_orders(self,symbol,cancel_orders):
        for order in cancel_orders:
            if order[2] == 'open_short':
                print(f"cancle: {order}")
                #self.cancel_short_entry_bitget(symbol)
            elif order[2] == 'open_long':
                print(f"cancle: {order}")
                #self.cancel_long_entry_bitget(symbol)

if __name__ == '__main__':
    symbol = 'ETHUSDT_UMCBL'
    marginCoin = 'USDT'
    # get leader
    ld = Leader("","","")

    # get follower
    fl = Follower("","","")
    while True:
        # get pct
        ld_dex = ld.get_balance_bitget(marginCoin)
        fl_dex = fl.get_balance_bitget(marginCoin)
        pct = round(float(fl_dex)/float(ld_dex) , 2)
        print(f"pct is {pct}")
    #     # check positions
        ld_positions = ld.get_positions_bitget(symbol)
        fl_positions = fl.get_positions_bitget(symbol)

        diff_long = fl.check_long_position(ld_positions,fl_positions)
        diff_short = fl.check_short_position(ld_positions,fl_positions)

    #     ## if partial not same , cut the size
        fl.cut_qty(diff_long,diff_short)


        # get ld orders
        ld_orders = ld.get_open_orders(symbol)
        print(ld_orders)

        # pct ld orders
        pct_orders = fl.get_pct_orders(pct,ld_orders)
        print(pct_orders)

        ## check open order if exist
        fl_orders = fl.get_open_orders(symbol)
        cancel_orders,exec_orders = fl.check_order_exist(pct_orders,fl_orders)

        ## cancel orders
        fl.cancel_orders(symbol,cancel_orders)

        ## exec orders
        print(exec_orders)
        ## copy trader
        if exec_orders != []:
            fl.copy_trade(symbol,exec_orders)


        time.sleep(5)

