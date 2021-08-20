import pandas as pd

df = pd.read_csv('transactions.csv', parse_dates=True, index_col=0)

df = df.sort_values(['time'])
df['commission'] = df['quantity']*0.8
trades = []

group = df.groupby(['instrument_code'])
count = 0
import pprint
for key, grouped_df in group:
    current_position = dict()
    for i, row in grouped_df.iterrows():
        if not current_position:
            current_position['instrument_code'] = row['instrument_code']
            current_position['start_time'] = row['time']
            current_position['current_quantity'] = row['quantity']
            current_position['commission'] = row['commission']
            current_position['transactions'] = [
                dict(time=row['time'], price=row['price'], quantity=row['quantity'])
            ]
        else:
            quantity = row['quantity']
            current_position['current_quantity'] += quantity
            current_position['commission'] += row['commission']

            if current_position['current_quantity'] == 0:
                current_position['end_time'] = row['time']
                current_position['transactions'].append(
                    dict(time=row['time'], price=row['price'], quantity=row['quantity'])
                )

                total_quantity = 0
                average_buy_price = 0
                average_sell_price = 0

                temp_df = pd.DataFrame(current_position['transactions'])
                temp_df['transaction_value'] = (temp_df['price'] * temp_df['quantity']).abs()

                buy_df = temp_df[temp_df['quantity'] > 0]
                sell_df = temp_df[temp_df['quantity'] < 0]

                total_quantity = buy_df['quantity'].sum()
                current_position['total_quantity'] = total_quantity
                current_position['average_buy_price'] = buy_df['transaction_value'].sum() / total_quantity
                current_position['average_sell_price'] = sell_df['transaction_value'].sum() / total_quantity

                trades.append(current_position)
                current_position = dict()
            else:
                current_position['transactions'].append(
                    dict(time=row['time'], price=row['price'], quantity=row['quantity'])
                )


import pprint
# pprint.pprint(trades)
d = pd.DataFrame(trades)
del d['transactions']
d['profit'] = (d['average_sell_price'] - d['average_buy_price']) * d['total_quantity']
d['final_profit'] = d['profit'] - d['commission']

d.to_csv('trades.csv')
print(d[['profit', 'final_profit', 'commission']])


# 3 * 100
# 4 * 104
# (100*3 + 4*104) / 7 =

