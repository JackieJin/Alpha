import pandas as pd
import quandl

from data.base_api import AbstractData
from math_utils import fillnan

auth_tok = '7rgk5sisbRwpDCDtUx9x'
vendor   = 'WIKI'


class QuandlData(AbstractData):

    def _rename_columns(self,data):
        dict = {'Ex-Dividend': 'Ex Dividend',
                "Adj. Open": "Adj Open",
                "Adj. Close": "Adj Close",
                "Adj. High": "Adj High",
                "Adj. Low": "Adj Low",
                "Adj. Volume": "Adj Volume"
                }
        if isinstance(data, pd.Panel):
            data = data.to_frame(filter_observations= False)
            titles = list(data)
            titles_new = [dict[t] if t in dict else t for t in titles]
            data.columns = titles_new
            data = data.to_panel()
        else:
            titles = list(data)
            titles_new = [dict[t] if t in dict else t for t in titles]
            data.columns = titles_new

        return data


    # def get_data(self, ticker, start_date, end_date):
    #     if type(ticker) == list:
    #         print(" start to download ticker %s from quandl" % ticker)
    #         d_dict = dict(zip(ticker,[quandl.get("%s/%s" % (vendor, t), trim_start=start_date, trim_end=end_date, authtoken=auth_tok) for t in ticker]))
    #         data = pd.Panel.from_dict(d_dict, orient= 'Minor')
    #         print(" ticker %s is  downloaded from" % ticker)
    #     else:
    #         data = quandl.get("%s/%s" % (vendor, ticker), trim_start=start_date, trim_end=end_date, authtoken=auth_tok)
    #
    #     data = self._rename_columns(data)
    #     if isinstance(data, pd.Panel):
    #         data = data.to_frame()
        return data

    def get_data(self, tickers, start_date, end_date):
        data = pd.DataFrame()
        for ticker in tickers:
            d = quandl.get("%s/%s" % (vendor, ticker), trim_start=start_date, trim_end=end_date, authtoken=auth_tok)
            d = self._rename_columns(d)
            d.columns = [ticker + '-'+ c for c in d.columns]
            data = data.combine(d, lambda a, b: fillnan(a, b))
        return data
if __name__ == '__main__':
    qd = QuandlData()
    tt2 = qd.get_data2(['AAPL', 'C'], '2000-1-1', '2017-1-1')
    print(tt2)