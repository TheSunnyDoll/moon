from pybitget import Client
import time

class Leader:
    def __init__(self,leaderKey,leaderSert,leaderPwd) -> None:
        self.key = leaderKey
        self.secret = leaderSert
        self.passphrase = leaderPwd


##
class Follower:
    def __init__(self,key,secret,passphrase) -> None:
        self.key = key
        self.secret = secret
        self.passphrase = passphrase


if __name__ == '__main__':
    marginCoin = 'USDT'

    ## get leader
    ld = Leader("bg_c45731ac5b26812eb9676f7bb0f23750","ca6f575af882d4af5fb0b3e45a0657c3756ec079d0ac522b0d63f7a06164af73","Zz123456")
    ld_client = Client(ld.key, ld.secret, passphrase=ld.passphrase)

    ## get follower
    fl = Follower("bg_2f2c7bcad16db7eaac00c52f162f5fe8","028bc30d5792376166d3c8e70c908bb188b06b4145acbba84911e767c3847814","aishuo999")
    fl_client = Client(fl.key, fl.secret, passphrase=fl.passphrase)

    while True:
        ld_dex = ld_client.mix_get_accounts(productType='UMCBL')['data'][0]['usdtEquity']
        # print(ld_dex)
        ## get orders
        result = ld_client.mix_get_all_open_orders('umcbl','USDT')['data']
        ld_infos = []
        for data in result:
            info = [data['symbol'],data['size'],data['price'],data['side']]
            ld_infos.append(info)
        # print(ld_infos)


        fl_dex = fl_client.mix_get_accounts(productType='UMCBL')['data'][0]['usdtEquity']
        # print(fl_dex)

        ## pct the orders
        fl_orders = []
        pct = round(float(fl_dex)/float(ld_dex) , 2)
        # print(pct)
        for info in ld_infos:
            order = info
            order[1] = round(info[1] * pct , 3)
            fl_orders.append(order)

        # print(fl_orders)

        ## check open order if exist
        result = fl_client.mix_get_all_open_orders('umcbl','USDT')['data']
        fl_infos = []
        for data in result:
            info = [data['symbol'],data['size'],data['price'],data['side']]
            fl_infos.append(info)

        cancel_orders = []
        exec_orders = fl_orders
        for info in fl_infos:
            for fo in fl_orders:
                if info == fo:
                    exec_orders.remove(fo)
                if fo not in fl_infos:
                    cancel_orders.append(fo)    

        # cacel orders

        # print(exec_orders)

        ## copy trader
        if exec_orders != []:
            for exo in exec_orders:
                # result = fl_client.mix_place_order(exo[0], marginCoin, exo[1], exo[3],'limit', price=exo[2])['msg']
                print(f"place order : {exo}")
                # print(result)
        
        # check positions
        ## if same , continue

        ## if not same , clear 

        ## if partial not same , cut the size

        time.sleep(5)


