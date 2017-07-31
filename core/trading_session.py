from __future__ import print_function
from datetime import datetime
from qstrader.compat import queue
from qstrader.event import EventType
from qstrader.price_handler.yahoo_daily_csv_bar import YahooDailyCsvBarPriceHandler
from qstrader.price_parser import PriceParser
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.tearsheet import TearsheetStatistics


class TradingSession(object):
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """
    def __init__(
        self, config, tickers,
        equity, start_date, end_date,
        session_type="backtest", end_session_time=None,
        portfolio_handler=None,
        compliance=None,
        execution_handler=None,
        title=None, benchmark=None
    ):
        """
        Set up the backtest variables according to
        what has been passed in.
        """
        self.config = config
        self.tickers = tickers
        self.equity = PriceParser.parse(equity)
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio_handler = portfolio_handler
        self.compliance = compliance
        self.execution_handler = execution_handler
        self.title = title
        self.benchmark = benchmark
        self.session_type = session_type
        self._config_session()
        self.cur_time = None

        if self.session_type == "live":
            if self.end_session_time is None:
                raise Exception("Must specify an end_session_time when live trading")

    def _config_session(self):
        """
        Initialises the necessary classes used
        within the session.
        """
        if self.price_handler is None and self.session_type == "backtest":
            self.price_handler = YahooDailyCsvBarPriceHandler(
                self.config.CSV_DATA_DIR, self.events_queue,
                self.tickers, start_date=self.start_date,
                end_date=self.end_date
            )

        if self.position_sizer is None:
            self.position_sizer = FixedPositionSizer()

        if self.risk_manager is None:
            self.risk_manager = ExampleRiskManager()

        if self.portfolio_handler is None:
            self.portfolio_handler = PortfolioHandler(
                self.equity,
                self.events_queue,
                self.price_handler,
                self.position_sizer,
                self.risk_manager
            )

        if self.compliance is None:
            self.compliance = ExampleCompliance(self.config)

        if self.execution_handler is None:
            self.execution_handler = IBSimulatedExecutionHandler(
                self.events_queue,
                self.price_handler,
                self.compliance
            )

        if self.statistics is None:
            self.statistics = TearsheetStatistics(
                self.config, self.portfolio_handler,
                self.title, self.benchmark
            )
        self._initilizeParameters()

    def _initilizeParameters(self):
        self.portfolio_handler.strategy.initialize(self.portfolio_handler)


    def _continue_loop_condition(self):
        if self.session_type == "backtest":
            return self.price_handler.continue_backtest
        else:
            return datetime.now() < self.end_session_time

    def _run_session(self):
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
                event = self.portfolio_handler.events_queue.get(False)
            except queue.Empty:
                self.stream_next()
            else:
                if event is not None:
                    if (
                        event.type == EventType.TICK or
                        event.type == EventType.BAR  or
                        event.type == EventType.TIME
                    ):
                        self.portfolio_handler.calculate_signals(event)
                    elif event.type == EventType.SIGNAL:
                        self.portfolio_handler.on_signals(event)
                    elif event.type == EventType.TARGETWEIGHT:
                        self.portfolio_handler.on_target_weights(event)
                    elif event.type == EventType.ORDER:
                        self.execution_handler.execute_order(event)
                    elif event.type == EventType.FILL:
                        self.portfolio_handler.on_fill(event)
                    elif event.type == EventType.RECON:
                        self.portfolio_handler.update_portfolio_value(event)
                    else:
                        raise NotImplemented("Unsupported event.type '%s'" % event.type)

    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self._run_session()
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

    def stream_next(self):
        event = self.portfolio_handler.stream_next()
        self.portfolio_handler.events_queue.put(event)