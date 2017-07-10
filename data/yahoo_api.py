
import pandas as pd
from pandas_datareader import data

from data.base_api import AbstractData


class YahooData(AbstractData):

    def get_data(self, ticker, start_date, end_date):
        d = data.get_data_yahoo(ticker, start_date, end_date)
        if isinstance(d, pd.Panel):
            d = d.to_frame()
        return d




if __name__ == '__main__':
    yahoo = YahooData()
    tt2 = yahoo.get_data(['AAPL', 'C'], '2000-1-1', '2017-1-1')
    print(tt2)