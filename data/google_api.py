import pandas as pd
from pandas_datareader import data

from data.base_api import AbstractData


class GoogleData(AbstractData):


    def get_data(self, ticker, start_date, end_date):
        d = data.DataReader(ticker, "google", start_date, end_date)
        if isinstance(d, pd.Panel):
            d = d.to_frame()
        return d

