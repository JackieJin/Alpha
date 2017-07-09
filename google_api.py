from pandas_datareader import data
import fix_yahoo_finance
from base_api import AbstractData
import pandas as pd

class GoogleData(AbstractData):


    def get_data(self, ticker, start_date, end_date):
        d = data.DataReader(ticker, "google", start_date, end_date)
        if isinstance(d, pd.Panel):
            d = d.to_frame()
        return d

