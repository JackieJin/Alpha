import datetime

import pandas as pd
import numpy as np

from data.data_factory import StockData
from data.get_data import get_data_from_db
from core.pool import PriceEventPool
from core.event import PriceEvent

class PriceHandler(object):
    def __init__(self, data_symbols, init_tickers=[], start_date = None, end_date= None, freq = 'B'):
        self.data_symbols       = data_symbols
        self.start_date         = start_date
        self.end_date           = end_date
        self.freq               = freq
        self.tickers            = []
        self.last_price_events  = []
        self.init_tickers       = init_tickers
        self.data               = None
        self.timestamp          = pd.date_range(self.start_date, self.end_date, freq=self.freq)
        self.curr_idx           = -1
        self.portfolio_handler  = None

    def initialize(self, portfolio_handler=None):
        self._get_initial_data()
        self.portfolio_handler = portfolio_handler
        timestamp = self.portfolio_handler.cur_time
        if self.portfolio_handler is not None:
            self.curr_idx = np.argmax(self.timestamp == timestamp)
        self._subscribe_tickers(timestamp)


    def get_current_timestamp(self):
        """
        Returns the most recent actual timestamp for a given ticker
        """
        return self.get_timestamp_by_idx(self.curr_idx)



    def get_timestamp_by_idx(self, idx):
        timestamp = self.timestamp[idx]
        return timestamp

    def stream_next(self):
        self.curr_idx += 1
        if self.curr_idx < len(self.timestamp):
            timestamp   = self.timestamp[self.curr_idx]
            self._subscribe_tickers(timestamp)
            price_events = self.tickers
        else:
            price_events = PriceEventPool(None)

        return price_events

    def istick(self):
        return False

    def get_last_close(self, ticker):
        price_event = self.tickers.pool[ticker]
        close_price = price_event.adj_price
        return close_price

    def continue_backtest(self):
        flag = True
        if self.curr_idx >= len(self.timestamp):
            flag = False
        return flag



    def _create_price_event(self, ticker, timestamp):
        try:
            row             = self.data.loc[timestamp, :]
            adj_close       = row[ticker + '-Adj Close']
            close           = row[ticker + '-Close']
        except(KeyError,):
            adj_close       = None
            close           = None

        if adj_close is None:
            adj_close = self.tickers.pool[ticker].adj_price
        if close is None:
            close     = self.tickers.pool[ticker].price

        event = PriceEvent(ticker, close, adj_close)
        return event

    def _subscribe_tickers(self, timestamp):

        event_pool = PriceEventPool(timestamp)
        for ticker in self.init_tickers:
            event = self._create_price_event(ticker, timestamp)
            event_pool.add(event)
        self.last_price_events  = self.tickers
        self.tickers            = event_pool

    def _get_initial_data(self):
        self.data = get_data_from_db(self.data, self.data_symbols, self.start_date, self.end_date)


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