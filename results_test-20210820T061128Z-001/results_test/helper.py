import pandas as pd
import os
import datetime
processed_data_path = 'D://datafiles imp//backtest'
def get_futures(expiry, symbol, result_date):
    directory_path = os.path.join(processed_data_path, symbol)
    base_name = symbol + '_' + str(expiry) + '_FUT' + '.csv'
    filepath = os.path.join(directory_path, base_name)
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    start_time = datetime.time(9, 15)
    end_time = datetime.time(15, 30)
    start_time = datetime.datetime.combine(result_date, start_time)
    end_time = datetime.datetime.combine(result_date, end_time)
    df = df[start_time:end_time]
    return df


def get_options(expiry, symbol, result_date, option_typ, strike_price):
    directory_path = os.path.join(processed_data_path, symbol)
    base_name = symbol + '_' + str(expiry) + '_OPT' + '_' + str(strike_price)+ '_' + option_typ + '.csv'
    filepath = os.path.join(directory_path, base_name)
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    start_time = datetime.time(9, 15)
    end_time = datetime.time(15, 30)
    start_time = datetime.datetime.combine(result_date, start_time)
    end_time = datetime.datetime.combine(result_date, end_time)
    df = df[start_time:end_time]
    return df



