from pybitget import Client
import pandas as pd
import streamlit as st
import time

class API:
    def __init__(self,key,secret,passphrase):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase


def get_all_client_api():
    clients=[]
    c0 = API("","","")
    clients.append(c0)
    c1 = API("","","")
    clients.append(c1)
    c2 = API("","","")
    clients.append(c2)
    return clients

def get_all_info_and_transfer():
    clents_info = []
    clients = get_all_client_api()
    for client in clients:
        con_client = Client(client.key, client.secret, passphrase=client.passphrase)
        result = con_client.spot_get_account_assets(coin='USDT')
        spot = result['data'][0]['available']
        if float(spot) > 2:
            spot = float(spot) - 1
            con_client.spot_transfer('spot', 'mix_usdt', spot, 'USDT', clientOrderId=None)
        positions = con_client.mix_get_all_positions('umcbl','USDT')
        p_pos = 0
        n_pos = 0
        for pos in positions['data']:
            if float(pos['margin']) > 0:
                if pos['holdSide'] == 'long':
                    p_pos += float(pos['margin']) * 10
                    print(pos)
                if pos['holdSide'] == 'short':
                    n_pos += float(pos['margin']) * 10

        future = con_client.mix_get_accounts(productType='UMCBL')
        ft_av = future['data'][0]['usdtEquity']
        ft_upl = future['data'][0]['unrealizedPL']

        p_pct = p_pos / float(ft_av) * 100 / 100
        n_pct = n_pos / float(ft_av) * 100 / 100
        p_pct = "%.2f%%" % (p_pct * 100)
        n_pct = "%.2f%%" % (n_pct * 100)

        total = float(spot) + float(ft_av)
        info = [total,spot,ft_av,ft_upl,p_pct,n_pct]
        clents_info.append(info)
    return clents_info

def get_list():
    infos = get_all_info_and_transfer()
    df = pd.DataFrame(
        infos,
        columns=[
            "总账户",
            "现货账户",
            "合约账户",
            "未实现盈亏",
            "多头仓位",
            "空头仓位"
        ],
        index=[
            "快速+解套",
            "快速",
            "单eth"
        ]

    )
    return df
    
st.write("""
# scalp product test
## initial fund   : 6k
   单向最大总仓     : 150%
   下单周期时间     : 30s
""")
data = get_list()
st.dataframe(data)
    

while True:
    time.sleep(120)
    st.experimental_rerun()