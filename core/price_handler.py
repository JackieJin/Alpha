import datetime

import pandas as pd

from data.data_factory import StockData
from data.get_data import get_data_from_db
from core.pool import EventPool

class PriceHandler(object):
    def __init__(self, data_symbols, init_tickers = None, start_date = None, end_date= None, freq = 'D'):
        self.data_symbols       = data_symbols
        self.start_date         = start_date
        self.end_date           = end_date
        self.freq               = freq
        self.tickers            = {}
        self.init_tickers       = init_tickers
        self.data               = None
        self.timestamp          = pd.date_range(self.start_date, self.end_date, freq=self.freq)
        self.curr_idx           = 0
        self.portfolio_handler  = None

    def initialize(self, portfolio_handler):
        self._get_initial_data()
        self.subscribe_tickers()
        self.portfolio_handler      = portfolio_handler

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
        except (KeyError,):
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
        event = EventPool(self.timestamp[self.curr_idx])
        self.subscribe_tickers()
        self.curr_idx += 1
        return event

    def istick(self):
        return False

    def get_last_close(self, ticker):
        close_price = self.tickers[ticker]["close"]
        return close_price

    def continue_backtest(self):
        flag = True
        if self.curr_idx >= len(self.timestamp):
            flag = False
        return flag


if __name__ == "__main__":
    start_date = datetime.datetime(1990, 1, 1)
    end_date = datetime.datetime.today()

    s1 = StockData('quandl', ['AAPL', 'C', 'GS'])
    s2 = StockData('google', ['SPY'])
    symbols = [s1, s2]
    tickers = ['AAPL', 'C', 'GS', 'SPY']
    ph = PriceHandler(symbols, tickers, start_date, end_date)
    ph.initialize()
    print(ph)