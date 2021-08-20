import pandas as pd
import nsepy
import datetime
start_date = datetime.date(2020, 1, 1)
end_date = datetime.date.today()

df = nsepy.get_history('BANKBARODA', start_date, end_date)
df.to_csv('BANKBARODA.csv')