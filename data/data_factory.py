
import datetime

from data.google_api import GoogleData
from data.quandl_api import QuandlData
from data.yahoo_api import YahooData
from math_utils import fillnan


class DataFactory:
    def get(self, vendor):
        if vendor == 'quandl':
            return QuandlData()
        elif vendor == 'yahoo':
            return YahooData()
        elif vendor == 'google':
            return GoogleData()
        else:
            return None


class StockData(object):
    def __init__(self,  vendor, tickers, fields = None):
        self.vendor     = vendor
        self.tickers    = tickers
        self.properties = fields

    def get_data(self,  start_date, end_date):
        data_factory = DataFactory()
        vendor = data_factory.get(self.vendor)
        data = vendor.get_data(self.tickers, start_date, end_date)
        return data


if __name__ == "__main__":
    # vendor_data = DataFactory()
    # q = vendor_data.get('quandl')
    # y = vendor_data.get('yahoo')
    # g = vendor_data.get('google')

    start_date = datetime.datetime(2014, 11, 1)
    end_date = datetime.datetime(2016, 10, 12)

    s1 = StockData('quandl', ['AAPL', 'C', 'GS'])
    d1 = s1.get_data(start_date,end_date)
    s2 = StockData('yahoo', ['SPY'])
    d2 = s2.get_data(start_date, end_date)

    d3 = d1.combine(d2, lambda a, b: fillnan(a, b))
    print(d3)
    # a = q.get_data(['AAPL','C'], start_date, end_date)
    # b = y.get_data('AAPL', start_date, end_date)
    # SPY = g.get_data(['SPY', 'AAPL'], start_date, end_date)
    # SPY.combine_first(a)
