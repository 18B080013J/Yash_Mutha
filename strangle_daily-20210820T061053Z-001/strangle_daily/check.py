import pandas as pd
df = pd.read_csv('3131.csv', index_col=0, parse_dates=True)

transactions = []
def _transact(row, quantity, reason, param='close'):
    temp = dict()
    temp['instrument_code'] = row['code']
    temp['time'] = row.name
    temp['price'] = row[param]
    temp['quantity'] = quantity
    temp['reason'] = reason
    transactions.append(temp)


def sell(row, quantity=-1, reason=None, ):
    _transact(row, quantity, reason, param)


def buy(row, quantity=1, reason=None):
    _transact(row, quantity, reason)
