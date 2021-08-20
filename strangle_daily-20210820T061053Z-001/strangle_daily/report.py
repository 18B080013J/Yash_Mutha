import pandas as pd
import numpy as np


trades = pd.read_csv('trades.csv', parse_dates=True)

trades['account'] = 10000 + trades['final_profit'].cumsum()
print(trades)

reports = []

total_trades = len(trades)
reports.append(dict(title='Total Trades', value=total_trades))

profit_trades = len(trades[trades['final_profit'] > 0])
loss_trades = len(trades[trades['final_profit'] < 0])

reports.append(dict(title='Profitable Trades', value=profit_trades))
reports.append(dict(title='Losing Trades', value=loss_trades))

trades['loss_count'] = np.where(trades['final_profit'] < 0, 1, 0)
trades['lc'] = (trades['loss_count'].diff(1) != 0).cumsum()
max_con_loss = trades[trades['loss_count'] == 1].groupby('lc').size().max()
max_con_profit = trades[trades['loss_count'] == 0].groupby('lc').size().max()

reports.append(dict(title='Max Con. Loss', value=max_con_loss))
reports.append(dict(title='Max Con. Profit', value=max_con_profit))
reports_df = pd.DataFrame(reports)
reports_df.to_csv('report.csv')