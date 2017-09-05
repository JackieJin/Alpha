import queue
from datetime import datetime

from core.event import EventType
from core.portfolio import Portfolio


class PortfolioHandler(object):

    def __init__(
        self, initial_cash, events_queue,
        price_handler, position_sizer,
        risk_manager, execution_handler,
        strategy, statistics, start_time
    ):

        self.initial_cash       = initial_cash
        self.events_queue       = events_queue
        self.price_handler      = price_handler
        self.position_sizer     = position_sizer
        self.risk_manager       = risk_manager
        self.execution_handler  = execution_handler
        self.portfolio          = Portfolio(initial_cash)
        self.strategy           = strategy
        self.statistics         = statistics
        self.cur_time           = start_time
        self.session_type       = "backtest"

    def initialize_parameters(self):
        self.price_handler.initialize(self)
        self.portfolio.initialize(self)
        self.strategy.initialize(self)
        self.execution_handler.initialize(self)
        if self.position_sizer is not None:
            self.position_sizer.initialize(self)

    def get_current_weights(self, ticker=None):
        if ticker is None:
            return self.portfolio.get_current_weights()
        else:
            return self.portfolio.get_current_weights(ticker)

    def get_current_timestamp(self):
        return self.price_handler.get_current_timestamp()


    def get_best_bid_ask(self, ticker):
        return self.price_handler.get_best_bid_ask(ticker)

    def get_last_close(self, ticker):
        return self.price_handler.get_last_close(ticker)

    def update_portfolio_value(self):
        self.portfolio.update_portfolio()


    def _stream_next(self):
        event         = self.price_handler.stream_next()
        self.cur_time = event.time
        self._place_events_onto_queue(event)

    def _calculate_signals(self, event):
        event = self.strategy.calculate_signals(event)
        self._place_events_onto_queue(event)

    def _convert_signals_to_order(self, weight_events):

        order_events = self.position_sizer.size_order(weight_events)
        self._place_events_onto_queue(order_events)

    def _on_suggested_order(self, order_events):
        order_events = self.execution_handler.execute_order(order_events)
        self._convert_fill_to_portfolio_update(order_events)


    def _continue_loop_condition(self):
        if self.session_type == "backtest":
            return self.price_handler.continue_backtest()
        else:
            return datetime.now() < self.end_session_time

    def _place_events_onto_queue(self, events):
        self.events_queue.put(events)

    def _convert_fill_to_portfolio_update(self, fill_events):
        for ticker in fill_events.pool:
            fill_event  = fill_events.pool[ticker]
            action      = fill_event.action
            ticker      = fill_event.ticker
            quantity    = fill_event.quantity
            price       = fill_event.price
            commission = 0
            # Create or modify the position from the fill info
            if fill_event.isvalid():
                self.portfolio.transact_position(
                    action, ticker, quantity,
                    price, commission
                )


    def run_session(self):

        if self.session_type == "backtest":
            print("Running Backtest...")
        else:
            print("Running Realtime Session until %s" % self.end_session_time)

        while self._continue_loop_condition():
            try:
                event_pool = self.events_queue.get(False)
            except queue.Empty:
                self._stream_next()
            else:
                if event_pool is not None:
                    if event_pool.type  == EventType.PRICE:
                        self._calculate_signals(event_pool)
                    elif event_pool.type == EventType.TARGETWEIGHT:
                        self._convert_signals_to_order(event_pool)
                    elif event_pool.type == EventType.ORDER:
                        self._on_suggested_order(event_pool)
                    else:
                        raise NotImplemented("Unsupported event_pool.type '%s'" % event_pool.type)
                    self.update_portfolio_value()

    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self.run_session()
        results = self.statistics.get_results()
        print("---------------------------------")
        print("Backtest complete.")
        print("Sharpe Ratio: %0.2f" % results["sharpe"])
        print(
            "Max Drawdown: %0.2f%%" % (
                results["max_drawdown_pct"] * 100.0
            )
        )
        if not testing:
            self.statistics.plot_results()
        return results
