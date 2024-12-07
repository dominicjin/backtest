import tushare as ts
import pandas as pd

def get_data(start_date, end_date, stock_code='000001.SZ'):
    pro = ts.pro_api('5234543bf3200c64ed8e45d81ef41fcbde23fba554ea0b485532fd0b')

    df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
    df = df.rename(columns={'trade_date':'date','vol':'volume'})
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index.astype(str), format='%Y%m%d')
    df = df.drop(columns=['ts_code'])
    df = df.iloc[::-1]

    df.to_csv('./data/data.csv', index='date')

if __name__ == "__main__":
    get_data('20180601', '20180731')