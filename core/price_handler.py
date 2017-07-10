import datetime

import pandas as pd

from data.data_factory import StockData
from data.get_data import get_data_from_db
from event import TimeEvent


class PriceHandler(object):
    def __init__(self, data_symbols, init_tickers = None, start_date = None, end_date= None, freq = 'D'):
        self.data_symbols   = data_symbols
        self.start_date     = start_date
        self.end_date       = end_date
        self.freq           = freq
        self.tickers        = {}
        self.init_tickers   = init_tickers
        self.data           = None

    def initialize(self):
        self.timestamp = pd.date_range(self.start_date, self.end_date, freq=self.freq)
        self.curr_idx  = 0
        self._get_initial_data()
        self.subscribe_tickers()

    def get_last_timestamp(self, ticker):
        """
        Returns the most recent actual timestamp for a given ticker
        """
        if ticker in self.tickers:
            timestamp = self.tickers[ticker]["timestamp"]
            return timestamp
        else:
            print(
                "Timestamp for ticker %s is not "
                "available from the %s." % (ticker, self.__class__.__name__)
            )
            return None

    def subscribe_ticker(self, ticker):
        timestamp = self.timestamp[self.curr_idx]
        try:
            row             = self.data.loc[(timestamp, ticker), :]
            close           = row['Close']
            adj_close       = row['Adj Close']
        except KeyError:
            close       = None
            adj_close   = None

        ticker_prices = {
            "close": close,
            "adj_close": adj_close,
            "timestamp": timestamp
        }
        self.tickers[ticker] = ticker_prices

    def subscribe_tickers(self):
        if self.init_tickers is not None:
            for ticker in self.init_tickers:
                self.subscribe_ticker(ticker)

    def _get_initial_data(self):
       self.data = get_data_from_db(self.data, self.data_symbols, self.start_date, self.end_date)

    def stream_next(self):
        event = TimeEvent(self.timestamp[self.curr_idx])
        self.curr_idx += 1
        self.subscribe_tickers()

        return event


if __name__ == "__main__":
    start_date = datetime.datetime(1990, 1, 1)
    end_date = datetime.datetime.today()

    s1 = StockData('quandl', ['AAPL', 'C', 'GS'])
    s2 = StockData('google', ['SPY'])
    data_symbols = [s1, s2]
    init_tickers = ['AAPL', 'C', 'GS', 'SPY']
    ph = PriceHandler(data_symbols, init_tickers, start_date,   end_date)
    ph.initialize()
    print(ph)