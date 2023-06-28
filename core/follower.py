from exchange.bitget import Bitget
import time

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


if __name__ == '__main__':
    symbol = 'ETHUSDT_UMCBL'
    marginCoin = 'USDT'
    # get leader
    ld = Leader("bg_c45731ac5b26812eb9676f7bb0f23750","ca6f575af882d4af5fb0b3e45a0657c3756ec079d0ac522b0d63f7a06164af73","Zz123456")

    # get follower
    fl = Follower("bg_2f2c7bcad16db7eaac00c52f162f5fe8","028bc30d5792376166d3c8e70c908bb188b06b4145acbba84911e767c3847814","aishuo999")
    while True:
        # get pct
        ld_dex = ld.get_balance_bitget(marginCoin)
        fl_dex = fl.get_balance_bitget(marginCoin)
        pct = round(float(fl_dex)/float(ld_dex) , 2)
        print(pct)
    #     # check positions
    #     ## if same , continue
        positions = ld.get_positions_bitget(symbol)
        print(positions)
    #     ## if not same , clear 

    #     ## if partial not same , cut the size



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

        ## exec orders

        print(fl_orders)
        ## copy trader
        if exec_orders != []:
            fl.copy_trade(symbol,exec_orders)


        time.sleep(5)

