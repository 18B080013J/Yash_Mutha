import os
import glob
import datetime
import pandas as pd

base_path = os.path.join(
    os.path.dirname(__file__),
    'data'
)

raw_data_path = os.path.join(base_path, 'raw')
inter_data_path = os.path.join(base_path, 'inter')
processed_data_path = 'D://datafiles imp//backtest//BANKNIFTY'


def get_raw_data():
    files = glob.glob("{}/*.csv".format(raw_data_path))

    results = []
    for _file in files:
        name = os.path.basename(_file)
        components = name.split('.')
        name = components[0]
        components = name.split('_')
        raw_date = components[-1]
        date = datetime.datetime.strptime(raw_date, '%d%m%Y').date()
        temp = dict()
        temp['file'] = _file
        temp['name'] = name
        temp['date'] = date
        results.append(temp)

    df = pd.DataFrame(data=results)
    df.sort_values(['date'], inplace=True)
    return df


def _get_base_data(path):
    files = glob.glob("{}/*.csv".format(path))

    _op = ['name', 'expiry', 'type', 'strike', 'option_type']
    _fut = ['name', 'expiry', 'type']

    results = []
    for _file in files:
        name = os.path.basename(_file)
        components, ext = os.path.splitext(name)
        name = components
        # BANKNIFTY_2019-01-03_OPT_23700.0_CE
        ex = name.split('_')
        if len(ex) == 3:
            temp = dict(zip(_fut, ex))
        else:
            temp = dict(zip(_op, ex))
        temp['file'] = _file
        temp['code'] = name
        results.append(temp)

    df = pd.DataFrame(results)
    df['expiry'] = pd.to_datetime(df['expiry'])
    df['strike'] = pd.to_numeric(df['strike'].fillna(0), errors='ignore')
    # df['name'] = df['file'].apply(lambda x: os.path.splitext(os.path.basename(x))[0])
    df.sort_values(['expiry', 'type', 'strike'], inplace=True)
    df.reset_index(inplace=True)
    return df


def get_inter_data():
    return _get_base_data(inter_data_path)


def get_processed_data():
    return _get_base_data(processed_data_path)


def get_df_from_row(row, start_date=None, end_date=None):
    _f = row['file']
    d = pd.read_csv(_f, parse_dates=True, index_col=0)

    if start_date:
        d = d[d.index >= pd.to_datetime(start_date)]

    if end_date:
        d = d[d.index <= pd.to_datetime(end_date)]
    d['code'] = row['code']
    d['file'] = row['file']
    return d.copy()
ohlc_dict = {
    'open':'first',
    'high':'max',
    'low':'min',
    'close':'last',
    'volume':'sum',
    'open_interest':'last'}


def pre_process(df):
    for i, row in df.iterrows():
        option_1min = get_df_from_row(row)
        file_name = option_1min['file'].unique()
        try:
            day_df = (option_1min.resample('5T').agg(ohlc_dict))
            day_df.dropna(inplace=True)
            day_df.to_csv(file_name[0])
        except:
            print('Error inn file')

def variable_add(df):
    for i, row in df.iterrows():
        option_1min = get_df_from_row(row)
        file_name = option_1min['file'].unique()
        try:
            day_df = (option_1min.resample('5T').agg(ohlc_dict))
            day_df.dropna(inplace=True)
            day_df.to_csv(file_name[0])
        except:
            print('Error inn file')




def get_5_min_data(df):
     df1 = (df.resample('5T').agg(ohlc_dict))
     df1.dropna(inplace=True)
     return df1


column_mappings = dict()
column_mappings['Open'] = 'open'
column_mappings['High'] = 'high'
column_mappings['Low'] = 'low'
column_mappings['Close'] = 'close'
column_mappings['Volume'] = 'volume'
column_mappings['Ticker'] = 'ticker'
column_mappings['Open Interest'] = 'open_interest'




