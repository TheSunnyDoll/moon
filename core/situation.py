# bj - 21:30 -- 1:00       utc :13:30 - 17:00         NY
#    - 2:30 - 5:00              18:30 - 21:00         LD
# 23:45 -00：45

# situation 
# - avoid trading [intraday session] before high impact news release (CPI/NFP/FOMC/PCE/GDP/PPI)
# 一定特别注意macro time
import pandas as pd
import json
import requests
from datetime import datetime

api_exchange_address = "https://www.deribit.com"

def get_book_summary_by_currency(currency, kind):
    url = "/api/v2/public/get_book_summary_by_currency"
    parameters = {'currency': currency, 'kind': kind}

    try:
        # 发送HTTPS GET请求
        json_response = requests.get((api_exchange_address + url + "?"), params=parameters)
        json_response.raise_for_status()  # 检查请求是否成功，如果不成功会抛出异常
        response_dict = json_response.json()
        instrument_details = response_dict["result"]
        return instrument_details
    except requests.exceptions.RequestException as e:
        print(f"请求异常：{e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解码错误：{e}")
        return None
    except KeyError as e:
        print(f"找不到指定的键：{e}")
        return None
def option_value_expiry(strike, size, underlying_price, option_type):
    # calculates the intrinsic value in dollars at expiry of a linear options

    if option_type == "C":
        option_value = max(0, underlying_price - strike) * size
    elif option_type == "P":
        option_value = max(0, strike - underlying_price) * size
    else:
        print("incorrect option type")
    return option_value

class Situation():
    def __init__(self) -> None:
        pass

    def fetch_data(self,currency):
        # fetch book summary and place into dataframe
        all_option_book_summary = get_book_summary_by_currency(currency, 'option')
        if all_option_book_summary == None:
            return None,None
        df = pd.DataFrame(all_option_book_summary)

        # split the instrument name into separate columns
        expiry_date = []
        strike_price = []
        option_type = []
        for index in range(len(df)):
            instrument_text = df.loc[index, 'instrument_name'].split('-')
            expiry_date.append(instrument_text[1])
            strike_price.append(float(instrument_text[2]))
            option_type.append(instrument_text[3])
        df = df.assign(expiry_date=expiry_date)
        df = df.assign(strike_price=strike_price)
        df = df.assign(option_type=option_type)

        unique_expiry_dates = df['expiry_date'].unique()
        unique_expiry_dates = sorted(unique_expiry_dates, key=lambda date: datetime.strptime(date, "%d%b%y"))
        return df, unique_expiry_dates


    def calculate_max_pain(self,df,selected_expiry):
        # create dataframe of selected expiry
        df_selected = df[df['expiry_date'] == selected_expiry]
        df_selected = df_selected.sort_values('strike_price')
        df_selected = df_selected.reset_index(drop=True)

        # create list of all expiry dates
        unique_strikes_selected = df_selected['strike_price'].unique()
        unique_strikes_selected.sort()

        # do max pain calculations for all options in the selected expiry
        max_pain_calcs = []
        for index in range(len(df_selected)):
            option_calc = {}
            for strike in unique_strikes_selected:
                option_calc[str(strike)] = option_value_expiry(df_selected.loc[index, 'strike_price'],
                                                            df_selected.loc[index, 'open_interest'],
                                                            strike,
                                                            df_selected.loc[index, 'option_type'])
            max_pain_calcs.append(option_calc)
        # create a dataframe out of the max pain calculations, merge it with the selected expiry dataframe
        df_max_pain_calcs = pd.DataFrame(max_pain_calcs)
        df_selected = pd.merge(df_selected, df_max_pain_calcs, left_index=True, right_index=True)
        return df_selected, unique_strikes_selected

def get_max_pains():
    st = Situation()
    df, unique_expiry_dates = st.fetch_data('BTC')
    if df.empty or unique_expiry_dates == None:
        return None
    max_pains = []
    for selected_expiry in unique_expiry_dates:
        df_selected, unique_strikes_selected = st.calculate_max_pain(df,selected_expiry)
        df_calls = df_selected[df_selected['option_type'] == 'C']
        total_intrinsic = []
        for strike in unique_strikes_selected:
            total_intrinsic.append(df_selected[str(strike)].sum())
        df_calls = df_calls.assign(total_intrinsic=total_intrinsic)
        max_pain_list = df_calls.loc[df_calls.total_intrinsic == df_calls['total_intrinsic'].min(), 'strike_price'].tolist()
        max_pain = max_pain_list[0]  # in case there are >1 strikes with the same intrinsic, select the first
        select_max_pain = [selected_expiry,max_pain]
        max_pains.append(select_max_pain)
    return max_pains

