import pandas as pd
from pandas_datareader import data

from data.base_api import AbstractData
from math_utils import fillnan

class GoogleData(AbstractData):


    # def get_data(self, ticker, start_date, end_date):
    #     d = data.DataReader(ticker, "google", start_date, end_date)
    #     if isinstance(d, pd.Panel):
    #         d = d.to_frame()
    #     return d

    def get_data(self, tickers, start_date, end_date):
        data = pd.DataFrame()
        for ticker in tickers:
            d           = data.DataReader(ticker, "google", start_date, end_date)
            d.columns   = [ticker + '-' + c for c in d.columns]
            data        = data.combine(d, lambda a, b: fillnan(a, b) )
        return data
