import requests
import json
import pandas as pd
import datetime
from helper import get_futures, get_options
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.dates as mdates
base_path = os.path.join(
    os.path.dirname(__file__),
    'data'
)
symbol = 'MARUTI'
url = 'https://opstra.definedge.com/api/resultscalendar/{}'
url = url.format(symbol)
month_expiries = [
    datetime.date(2016, 7, 28), datetime.date(2016, 8, 25), datetime.date(2016, 9, 29), datetime.date(2016, 10, 27),
    datetime.date(2016, 11, 24),
    datetime.date(2016, 12, 29), datetime.date(2017, 1, 25), datetime.date(2017, 2, 23), datetime.date(2017, 3, 30),
    datetime.date(2017, 4, 27),
    datetime.date(2017, 5, 25), datetime.date(2017, 6, 29), datetime.date(2017, 7, 27), datetime.date(2017, 8, 31),
    datetime.date(2017, 9, 28),
    datetime.date(2017, 10, 26), datetime.date(2017, 11, 30), datetime.date(2017, 12, 28), datetime.date(2018, 1, 25),
    datetime.date(2018, 2, 22),
    datetime.date(2018, 3, 28), datetime.date(2018, 4, 26), datetime.date(2018, 5, 31), datetime.date(2018, 6, 28),
    datetime.date(2018, 7, 26),
    datetime.date(2018, 8, 30), datetime.date(2018, 9, 27), datetime.date(2018, 10, 25), datetime.date(2018, 11, 29),
    datetime.date(2018, 12, 27),
    datetime.date(2019, 1, 31), datetime.date(2019, 2, 28), datetime.date(2019, 3, 28), datetime.date(2019, 4, 25),
    datetime.date(2019, 5, 30),
    datetime.date(2019, 6, 27), datetime.date(2019, 7, 25), datetime.date(2019, 8, 29), datetime.date(2019, 9, 26),
    datetime.date(2019, 10, 31),
    datetime.date(2019, 11, 28), datetime.date(2019, 12, 26), datetime.date(2020, 1, 30), datetime.date(2020, 2, 27),
    datetime.date(2020, 3, 26),
    datetime.date(2020, 4, 30), datetime.date(2020, 5, 28), datetime.date(2020, 6, 25), datetime.date(2020, 7, 30),
    datetime.date(2020, 8, 27),
    datetime.date(2020, 9, 24), datetime.date(2020, 10, 29), datetime.date(2020, 11, 26), datetime.date(2020, 12, 31),
    datetime.date(2021, 1, 28),
    datetime.date(2021, 2, 25), datetime.date(2021, 3, 25), datetime.date(2021, 4, 29), datetime.date(2021, 5, 27),
    datetime.date(2021, 6, 24),
    datetime.date(2021, 7, 29), datetime.date(2021, 8, 26), datetime.date(2021, 9, 30), datetime.date(2021, 10, 28),
    datetime.date(2021, 11, 25),
    datetime.date(2021, 12, 30)
]
response = requests.get(url)
if response.status_code == 200:
    _file = json.loads(response.text)
    for dicts in _file:
        if int(dicts['Year']) >= 2017:
            result_time = dicts['Time']
            result_year = dicts['Year']
            result_typ = dicts['Quarter']
            result_date = pd.to_datetime(dicts['Date']).date()
            an_iterator = filter(lambda date: date >= result_date, month_expiries)
            filtered_expiries = list(an_iterator)
            expiry = filtered_expiries[0]
            df = get_futures(expiry, symbol, result_date)
            time = datetime.time(9, 20)
            straddle_price = df.loc[datetime.datetime.combine(result_date, time)]['close']
            straddle_price = float(round((straddle_price/100))*100)
            options_df_ce = get_options(expiry, symbol, result_date, 'CE', straddle_price)
            options_df_pe = get_options(expiry, symbol, result_date, 'PE', straddle_price)
            straddle_df = options_df_ce['close'] + options_df_pe['close']
            straddle_df = pd.DataFrame(straddle_df)
            straddle_df['time'] = straddle_df.index.time
            straddle_df['time'] = straddle_df['time'].apply(lambda x: x.strftime('%H:%M'))
            straddle_df.set_index(straddle_df['time'], inplace=True)

            plt.plot(straddle_df.index, straddle_df['close'])
            save_path = os.path.join(base_path, 'graphs')
            csv_path = os.path.join(base_path, 'data_file')
            fig_name = result_year + result_typ
            csv_name = fig_name + '.csv'
            csv_path = os.path.join(csv_path, csv_name)
            straddle_df.to_csv(csv_path)
            fig = plt.figure(figsize=(30, 10))
            fig, ax = plt.subplots()
            ax.plot(straddle_df['time'], straddle_df['close'])

            fig_path = os.path.join(save_path, fig_name)
            plt.savefig(fig_path)





