import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime
intrade_df = pd.read_csv('in_trade_df.csv', index_col=0, parse_dates=True)
i = 1
while i < 10:
    intrade_df = intrade_df[intrade_df['trade_no'] == i]
    ohlc_df = intrade_df[['open', 'high', 'low', 'close', 'volume']]
    date = ohlc_df.index[0].date()
    apdict = mpf.make_addplot(intrade_df['stop_loss'])
    mpf.plot(ohlc_df, volume=True, addplot=apdict, type='candle', style='charles', title='02-02-2018')
    exit()




