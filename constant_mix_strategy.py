
from qstrader import settings
from qstrader.strategy.base import AbstractStrategy
from qstrader.event import EventType, TargetWeightEvent
from qstrader.utils import date_utils
from qstrader.position_sizer.rebalance import ConstantPositionSizer
from qstrader.compat import queue
from qstrader.trading_session import TradingSession
from qstrader.price_handler.quandl_data import QuandlPriceHandler
import datetime

class ConstantMixStrategy(AbstractStrategy):
    def __init__(
      self, tickers_and_weights,
            events_queue,
    ):
        self.tickers_and_weights = tickers_and_weights
        self.events_queue = events_queue

    def calculate_signals(self, event):
        if (
            event.type == EventType.BAR and
            event.ticker in self.tickers_and_weights and
            date_utils._end_of_month(event.time)
        ):
            ticker = event.ticker
            if self.portfolio_handler.get_current_weight(ticker) !=\
                self.tickers_and_weights[ticker]:
                twe = TargetWeightEvent(ticker, self.tickers_and_weights[ticker])
                self.events_queue.put(twe)


def run(config, testing, tickers, ticker_weights):
    # Backtest information
    title = [
        'Monthly Liquidate/Rebalance on 60%/40% AAPL/GS Portfolio'
    ]
    initial_equity = 1000000.0
    start_date = datetime.datetime(2000, 11, 1)
    end_date = datetime.datetime(2016, 10, 12)
    tickers_and_weights = dict(zip(tickers, ticker_weights))

    # Use the Monthly Liquidate And Rebalance strategy

    events_queue = queue.Queue()
    strategy = ConstantMixStrategy(
        tickers_and_weights, events_queue
    )

    # Use the liquidate and rebalance position sizer
    # with prespecified ticker weights

    position_sizer = ConstantPositionSizer()
    tickers_and_weights = dict(zip(tickers, ticker_weights))
    tickers_and_vendors = dict(zip(tickers, ['WIKI']*len(tickers)))
    qph = QuandlPriceHandler(events_queue, tickers_and_vendors, '1960-1-1', '2017-6-14', True)
    qph.initilize()

    # Set up the backtest
    backtest = TradingSession(
        config, strategy, tickers,
        initial_equity, start_date, end_date,
        events_queue, position_sizer=position_sizer,
        title=title, benchmark=tickers[0], price_handler= qph
    )
    results = backtest.start_trading(testing=testing)
    return results


if __name__ == "__main__":

    # Configuration data
    testing = False
    config = settings.from_file(
        settings.DEFAULT_CONFIG_FILENAME, testing
    )
    tickers = ["AAPL", "AMZN"]
    weights = [0.6  ,  0.4 ]
    filename = None
    run(config, testing, tickers,weights)