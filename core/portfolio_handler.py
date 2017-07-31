import queue
from datetime import datetime

from core.event import EventType, OrderEvent
from core.portfolio import Portfolio


class PortfolioHandler(object):
    def __init__(
        self, tickers, initial_cash, events_queue,
        price_handler, position_sizer,
        risk_manager, execution_handler,
        strategy, statistics
    ):
        """
        The PortfolioHandler is designed to interact with the
        backtesting or live trading overall event-driven
        architecture. It exposes two methods, on_signal and
        on_fill, which handle how SignalEvent and FillEvent
        objects are dealt with.

        Each PortfolioHandler contains a Portfolio object,
        which stores the actual Position objects.

        The PortfolioHandler takes a handle to a PositionSizer
        object which determines a mechanism, based on the current
        Portfolio, as to how to size a new Order.

        The PortfolioHandler also takes a handle to the
        RiskManager, which is used to modify any generated
        Orders to remain in line with risk parameters.
        """
        self.initial_cash       = initial_cash
        self.events_queue       = events_queue
        self.price_handler      = price_handler
        self.position_sizer     = position_sizer
        self.risk_manager       = risk_manager
        self.execution_handler  = execution_handler
        self.portfolio          = Portfolio(price_handler, initial_cash, tickers)
        self.strategy           = strategy
        self.statistics         = statistics
        self.cur_time           = None
        self.session_type       = "backtest"

    def initialize_parameters(self):
        self.price_handler.initialize(self)
        self.portfolio.initialize(self)
        self.strategy.initialize(self)
        self.execution_handler.initialize(self)
        if self.position_sizer is not None:
            self.position_sizer.initialize(self)

    def on_signals(self, signal_event):
        """
        This is called by the backtester or live trading architecture
        to form the initial orders from the SignalEvent.

        These orders are sized by the PositionSizer object and then
        sent to the RiskManager to verify, modify or eliminate.

        Once received from the RiskManager they are converted into
        full OrderEvent objects and sent back to the events queue.
        """
        # Create the initial order list from a signal event
        initial_order = self._create_order_from_signal(signal_event)
        # Size the quantity of the initial order
        sized_order = self.position_sizer.size_order(
            self.portfolio, initial_order
        )
        # Refine or eliminate the order via the risk manager overlay
        order_events = self.risk_manager.refine_orders(
            self.portfolio, sized_order
        )
        # Place orders onto events queue
        self._place_orders_onto_queue(order_events)

    def on_target_weights(self, weight_events):
        """
        This is called by the backtester or live trading architecture
        to form the initial orders from the SignalEvent.

        These orders are sized by the PositionSizer object and then
        sent to the RiskManager to verify, modify or eliminate.

        Once received from the RiskManager they are converted into
        full OrderEvent objects and sent back to the events queue.
        """
        order_events = self.position_sizer.size_order(weight_events)

        # Refine or eliminate the order via the risk manager overlay
        # order_events = self.risk_manager.refine_orders(
        #     self.portfolio, sized_order
        # )
        # Place orders onto events queue
        self._place_orders_onto_queue(order_events)

    def on_suggested_order(self, order_events):
        order_events = self.execution_handler.execute_order(order_events)
        self._place_orders_onto_queue(order_events)

    def on_fill(self, fill_events):
        """
        This is called by the backtester or live trading architecture
        to take a FillEvent and update the Portfolio object with new
        or modified Positions.

        In a backtesting environment these FillEvents will be simulated
        by a model representing the execution, whereas in live trading
        they will come directly from a brokerage (such as Interactive
        Brokers).
        """
        self._convert_fill_to_portfolio_update(fill_events)

    def update_portfolio_value(self):
        """
        Update the portfolio to reflect current market value as
        based on last bid/ask of each ticker.
        """
        self.portfolio.update_portfolio()

    def calculate_signals(self, event):
        event = self.strategy.calculate_signals(event)
        self.strategy.save_signals(event)

    def get_current_weights(self, ticker=None):
        if ticker is None:
            return self.portfolio.get_current_weights()
        else:
            return self.portfolio.get_current_weights(ticker)


    def get_last_timestamp(self, ticker):
        return self.price_handler.get_last_timestamp(ticker)


    def stream_next(self):
        event = self.price_handler.stream_next()
        self.cur_time = event.time
        self.events_queue.put(event)

    def get_best_bid_ask(self, ticker):
        return self.price_handler.get_best_bid_ask(ticker)

    def get_last_close(self, ticker):
        return self.price_handler.get_last_close(ticker)


    def _continue_loop_condition(self):
        if self.session_type == "backtest":
            return self.price_handler.continue_backtest()
        else:
            return datetime.now() < self.end_session_time

    def _create_order_from_signal(self, signal_event):
        """
        Take a SignalEvent object and use it to form a
        SuggestedOrder object. These are not OrderEvent objects,
        as they have yet to be sent to the RiskManager object.
        At this stage they are simply "suggestions" that the
        RiskManager will either verify, modify or eliminate.
        """
        ticker = signal_event.ticker
        if signal_event.suggested_quantity is None:
            quantity = None
            action = None
        else:
            quantity = signal_event.suggested_quantity
            action = signal_event.action
        order = OrderEvent(
            ticker,
            action,
            quantity
        )
        return order

    def _place_orders_onto_queue(self, order_events):
        """
        Once the RiskManager has verified, modified or eliminated
        any order objects, they are placed onto the events queue,
        to ultimately be executed by the executionHandler.
        """
        self.events_queue.put(order_events)

    def _convert_fill_to_portfolio_update(self, fill_events):
        """
        Upon receipt of a FillEvent, the PortfolioHandler converts
        the event into a transaction that gets stored in the Portfolio
        object. This ensures that the broker and the local portfolio
        are "in sync".

        In addition, for backtesting purposes, the portfolio value can
        be reasonably estimated in a realistic manner, simply by
        modifying how the executionHandler object handles slippage,
        transaction costs, liquidity and market impact.
        """
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
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        if self.session_type == "backtest":
            print("Running Backtest...")
        else:
            print("Running Realtime Session until %s" % self.end_session_time)

        while self._continue_loop_condition():
            try:
                event_pool = self.events_queue.get(False)
            except queue.Empty:
                self.stream_next()
            else:
                if event_pool is not None:
                    if (
                        event_pool.type  == EventType.TICK or
                        event_pool.type  == EventType.BAR  or
                        event_pool.type  == EventType.TIME
                    ):
                        self.calculate_signals(event_pool)
                    elif event_pool.type == EventType.SIGNAL:
                        self.on_signals(event_pool)
                    elif event_pool.type == EventType.TARGETWEIGHT:
                        self.on_target_weights(event_pool)
                    elif event_pool.type == EventType.ORDER:
                        self.on_suggested_order(event_pool)
                    elif event_pool.type == EventType.FILL:
                        self.on_fill(event_pool)
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
