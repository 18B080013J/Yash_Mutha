from helper import get_processed_data, get_df_from_row, pre_process, get_5_min_data
import numpy as np
import datetime
import talib
import pandas as pd
import s3fs
weekly_expiry = []
all_df = get_processed_data()



st = datetime.date(2021, 1, 1)
en = datetime.date(2021, 7, 29)



all_df['expiry'] = all_df['expiry'].apply(lambda x: x.date())

futures_df = all_df[all_df['type'] == 'FUT']
futures_files = futures_df['file'].unique()
complete_df = pd.DataFrame()

for _file in futures_files:
    df = pd.read_csv(_file, index_col=0, parse_dates=True)
    df = df[(df['ticker'] == 'BANKNIFTY-I') | (df['ticker'] == 'BANKNIFTY-I.NFO')]
    df['ticker'] = 'BANKNIFTY-I'
    complete_df = pd.concat([complete_df, df])

bnf_5 = get_5_min_data(complete_df)



options_df = all_df[all_df['type'] == 'OPT']

options_df.to_csv('options.csv')

weekly_expiry_dates = options_df['expiry'].unique()
monthly_expiry_dates = futures_df['expiry'].unique()

for i, row in bnf_5.iterrows():
    if i.date() in weekly_expiry_dates:
        bnf_5.at[i, 'expiry'] = i.date()
expiry_bfill = bnf_5['expiry'].bfill()


bnf_5['expiry'] = np.where(
        bnf_5['expiry'].isnull(), expiry_bfill, bnf_5['expiry']
    )

bnf_5['RSI'] = talib.RSI(bnf_5['close'])


start = datetime.datetime(year=2019, month=1, day=1)

ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'open_interest': 'last',
    'volume': 'sum',
}

exchange_start_time = datetime.time(minute=15, hour=9)




def get_option_from_strike(strike, option_type, expiry):
    opt = options_df[
        (options_df['strike'] == strike) &
        (options_df['expiry'] == expiry) &
        (options_df['option_type'] == option_type)
        ]
    return opt.iloc[0]



positions = dict()
transactions = []


def _transact(row, quantity, reason, param='close', price=0, price_given=False):
    temp = dict()
    temp['instrument_code'] = row['code']
    temp['time'] = row.name
    if price_given:
        temp['price'] = price
    else:
        temp['price'] = row[param]
    temp['quantity'] = quantity
    temp['reason'] = reason
    transactions.append(temp)


def sell(row, quantity=-1, reason=None, param='close', price=0, price_given=False):
    _transact(row, quantity, reason, param, price, price_given)


def buy(row, quantity=1, reason=None):
    _transact(row, quantity, reason)

def weekly_to_monthly(weekly_date):
    for expiry_day in monthly_expiry_dates:
        if expiry_day.month == weekly_date.month:
            return expiry_day


def vwap(df):
    current_date = datetime.date(2017, 1, 1)
    previous_date = datetime.date(2016, 12, 31)
    for i, row in df.iterrows():  # need to intialise yest_close, day_close, today_high
        current_date = i.date()
        if current_date == previous_date:  # inside the same day 9:16 to 3:30

            ##############Calculating Vwap###############
            typ_p = (row['open'] + row['high'] + row['close']) / 3
            cummulative_volume = cummulative_volume + row['volume']
            cummulative_sum = cummulative_sum + typ_p * row['volume']
            if cummulative_volume == 0:
                df.at[i, 'vwap'] = 0
            else:
                df.at[i, 'vwap'] = cummulative_sum / cummulative_volume
        else:  # at 9:15
            # Calculating Vwap
            typ_p = (row['open'] + row['high'] + row['close']) / 3
            cummulative_volume = row['volume']
            cummulative_sum = typ_p * cummulative_volume
            if cummulative_volume == 0:
                df.at[i, 'vwap'] = 0
            else:
                df.at[i, 'vwap'] = cummulative_sum / cummulative_volume
        previous_date = current_date
    return df



capital = 200000
risk = 5000
def conditions_check(df, time):
    if df.loc[time]['RSI'] > 60 and df.loc[time]['vwap'] > df.loc[time]['close']:
        if df.loc[time]['open_interest'] < df.loc[time]['previous_open_interest'] and df.loc[time]['volume'] > df.loc[time]['volume_sma']:
            return True

        else:
            return False
    else:
        return False

position = False
rr_reached = False
count = 1

in_trade_df = pd.DataFrame()
bnf_5.dropna(inplace=True)

bnf_5 = bnf_5[st:en]




for i, row in bnf_5.iterrows():
    try:
        if not position:
            if row['RSI'] > 20 and i.time() > datetime.time(9, 19):
                close_price = row['close']
                strike_price = (round(close_price/100))*100
                expiry = row['expiry']
                instrument_row = get_option_from_strike(strike_price, 'CE', expiry)
                instrument_df = get_df_from_row(instrument_row)
                instrument_df['RSI'] = talib.RSI(instrument_df['close'])

                instrument_df['volume_sma'] = talib.SMA(instrument_df['volume'], timeperiod=20)
                instrument_df['previous_open_interest'] = instrument_df['open_interest'].shift(1)
                instrument_df = vwap(instrument_df)

                if i in instrument_df.index:
                    if conditions_check(df=instrument_df, time=i) and not position:
                        print(i, 'Code is Running', 'CE')
                        buy_df = instrument_df
                        buy(buy_df.loc[i], quantity=50, reason='BUY CE Triggered')
                        buy_price = buy_df.loc[i]['close']
                        init_stop_loss = buy_df.loc[i]['vwap'] - 30
                        stop_loss = init_stop_loss
                        in_trade_df = in_trade_df.append(buy_df.loc[i])
                        in_trade_df.at[i, 'stop_loss'] = stop_loss
                        in_trade_df.at[i, 'trade_no'] = count
                        position = True
            if row['RSI'] < 80 and i.time() > datetime.time(9, 19):#########PE Buying
                close_price = row['close']
                strike_price = (round(close_price / 100)) * 100
                expiry = row['expiry']
                instrument_row = get_option_from_strike(strike_price, 'PE', expiry)
                instrument_df = get_df_from_row(instrument_row)
                instrument_df['RSI'] = talib.RSI(instrument_df['close'])

                instrument_df['volume_sma'] = talib.SMA(instrument_df['volume'], timeperiod=20)
                instrument_df = vwap(instrument_df)
                instrument_df['previous_open_interest'] = instrument_df['open_interest'].shift(1)
                if i in instrument_df.index:
                    if conditions_check(df=instrument_df, time=i) and not position:
                        print(i, 'Code is Running', 'PE')
                        buy_df = instrument_df
                        buy(buy_df.loc[i], quantity=50, reason='BUY CE Triggered')
                        buy_price = buy_df.loc[i]['close']
                        init_stop_loss = buy_df.loc[i]['vwap'] - 40
                        stop_loss = init_stop_loss
                        in_trade_df = in_trade_df.append(buy_df.loc[i])
                        in_trade_df.at[i, 'stop_loss'] = stop_loss
                        in_trade_df.at[i, 'trade_no'] = count
                        position = True

        elif position:
            in_trade_df = in_trade_df.append(buy_df.loc[i])
            in_trade_df.at[i, 'stop_loss'] = stop_loss
            in_trade_df.at[i, 'trade_no'] = count
            current_close = buy_df.loc[i]['close']
            if i.time() == datetime.time(15, 25):
                sell(buy_df.loc[i], quantity=-50, reason='Time Over')
                position = False
                count = count + 1
            if i.time() == datetime.time(15, 25) and rr_reached and position:
                sell(buy_df.loc[i], quantity=-25, reason='Time Over')
                position = False
                rr_reached = False
                count = count + 1
            if stop_loss > buy_df.loc[i]['low'] and not rr_reached and position:
                sell(buy_df.loc[i], quantity=-50, reason='First SL Hit', price=stop_loss, price_given=True)
                position = False
                count = count + 1
            if buy_df.loc[i]['close'] > (buy_price + buy_price-init_stop_loss) and not rr_reached and position:##1:1 RR
                stop_loss = buy_price
                sell(buy_df.loc[i], quantity=-25, reason='Half Profit Booked')
                rr_reached = True
            if stop_loss > buy_df.loc[i]['low'] and rr_reached and position:
                sell(buy_df.loc[i], quantity=-25, reason='Trail SL Hit', price=stop_loss, price_given=True)
                rr_reached = False
                previous_close = current_close
                position = False
                count = count + 1
            if rr_reached:
                stop_loss = buy_df.loc[i]['open']
    except:
        print('Error in', i)


in_trade_df.to_csv('in_trade_df.csv')
transactions = pd.DataFrame(transactions)

# del transactions['instrument_code']
transactions.to_csv('transactions.csv')
# print(transactions/)



