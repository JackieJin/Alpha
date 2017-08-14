
import date_utils
from core.pool import WeightEventPool


class ConstantMixStrategy(object):
    def __init__(self, tickers_and_weights):
        self.tickers_and_weights = tickers_and_weights

    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def calculate_signals(self, event):
        if self._is_rebalance(event.time):
            twe = WeightEventPool(event.time)
            twe.add_weights(self.tickers_and_weights)
            return twe

    def _is_rebalance(self, time):
        return date_utils._end_of_month(time)
