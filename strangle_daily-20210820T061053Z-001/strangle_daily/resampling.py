import pandas as pd

df= pd.read_csv('banknifty5min.csv', index_col=0, parse_dates=True)


ohlc_dict = {
    'open':'first',
    'high':'max',
    'low':'min',
    'close':'last',
    'volume':'sum'
    }

day_df = (df.resample('D').agg(ohlc_dict))
day_df.dropna(inplace = True)
print(day_df)

