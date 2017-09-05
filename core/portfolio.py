
from core.position import Position
import pandas as pd
import numpy as np

class Portfolio(object):
    def __init__(self, cash):
        """
        On creation, the Portfolio object contains no
        positions and all values are "reset" to the initial
        cash, with no PnL - realised or unrealised.

        Note that realised_pnl is the running tally pnl from closed
        positions (closed_pnl), as well as realised_pnl
        from currently open positions.
        """

        self.init_cash              = cash
        self.total_mkt_value        = cash
        self.cur_cash               = cash
        self.closed_positions       = []
        self.realised_pnl           = 0
        self.unrealised_pnl         = 0

        self.portfolio_handler      = None
        self.statistics             = pd.DataFrame(columns=['total_mkt_value', 'cash'])
        self.quantities             = pd.DataFrame()
        self.weights                = pd.DataFrame()
        self.positions              = {}
        # self._init_positions(tickers)

    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def update_portfolio(self):
        """
        Updates the value of all positions that are currently open.
        Value of closed positions is tallied as self.realised_pnl.
        """

        # self.equity = self.realised_pnl
        self.total_mkt_value         = self.init_cash
        self.realised_pnl   = 0
        self.unrealised_pnl = 0

        for ticker in self.positions:
            pt = self.positions[ticker]
            # if self.price_handler.istick():
            #     bid, ask    = self.portfolio_handler.get_best_bid_ask(ticker)

            close_price = self.portfolio_handler.get_last_close(ticker)
            bid         = close_price
            ask         = close_price

            pt.update_market_value(bid, ask)
            # self.unrealised_pnl += pt.unrealised_pnl
            # self.realised_pnl   += pt.realised_pnl
            self.total_mkt_value         += pt.total_pnl

        self.statistics.loc[self.portfolio_handler.cur_time] =\
            [self.total_mkt_value, self.cur_cash]

        idx = pd.MultiIndex.from_product([[self.portfolio_handler.cur_time], list(self.positions.keys())],names = ['date', 'asset'] )
        qt  = [self.positions[ticker].net for ticker in self.positions]
        wt  = [self.get_current_weights(ticker) for ticker in self.positions]

        self.weights    = self.weights.append(pd.DataFrame(np.array([wt]).transpose(), index = idx, columns = 'weight'))
        self.quantities = self.quantities.append(pd.DataFrame(np.array([qt]).transpose(), index=idx, columns='weight'))

        # self.quantities.loc[self.portfolio_handler.cur_time] = [self.positions[ticker].net for ticker in self.positions]
        # self.weights.loc[self.portfolio_handler.cur_time] = [self.get_current_weights(ticker) for ticker in self.positions]

    # def _init_positions(self, tickers):
    #     for ticker in tickers:
    #         self.positions[ticker] = Position(ticker)

    # def _add_position(
    #     self, action, ticker,
    #     quantity, price, commission
    # ):
    #     """
    #     Adds a new Position object to the Portfolio. This
    #     requires getting the best bid/ask price from the
    #     price handler in order to calculate a reasonable
    #     "market value".
    #
    #     Once the Position is added, the Portfolio values
    #     are updated.
    #     """
    #     if ticker not in self.positions:
    #         # if self.price_handler.istick():
    #         #     bid, ask    = self.price_handler.get_best_bid_ask(ticker)
    #         # else:
    #         #     close_price = self.price_handler.get_last_close(ticker)
    #         #     bid         = close_price
    #         #     ask         = close_price
    #         # position = Position(
    #         #     ticker, action, quantity,
    #         #     price, commission, bid, ask
    #         # )
    #         position = Position(
    #             ticker, action, quantity,
    #             price, commission
    #         )
    #         self.positions[ticker] = position
    #         self.update_portfolio()
    #     else:
    #         print(
    #             "Ticker %s is already in the positions list. "
    #             "Could not add a new position." % ticker
    #         )
    #
    # def _modify_position(
    #     self, action, ticker,
    #     quantity, price, commission
    # ):
    #     """
    #     Modifies a current Position object to the Portfolio.
    #     This requires getting the best bid/ask price from the
    #     price handler in order to calculate a reasonable
    #     "market value".
    #
    #     Once the Position is modified, the Portfolio values
    #     are updated.
    #     """
    #     if ticker in self.positions:
    #         self.positions[ticker].transact_shares(
    #             action, quantity, price, commission
    #         )
    #         # if self.price_handler.istick():
    #         #     bid, ask    = self.price_handler.get_best_bid_ask(ticker)
    #         # else:
    #         #     close_price = self.price_handler.get_last_close(ticker)
    #         #     bid         = close_price
    #         #     ask         = close_price
    #         # self.positions[ticker].update_market_value(bid, ask)
    #
    #         # if self.positions[ticker].net == 0:
    #         #     closed = self.positions.pop(ticker)
    #         #     self.realised_pnl += closed.realised_pnl
    #         #     self.closed_positions.append(closed)
    #
    #         self.update_portfolio()
    #     else:
    #         print(
    #             "Ticker %s not in the current position list. "
    #             "Could not modify a current position." % ticker
    #         )

    def transact_position(
        self, action, ticker,
        quantity, price, commission
    ):
        """
        Handles any new position or modification to
        a current position, by calling the respective
        _add_position and _modify_position methods.

        Hence, this single method will be called by the
        PortfolioHandler to update the Portfolio itself.
        """

        if action == "BOT":
            self.cur_cash -= ((quantity * price) + commission)
        elif action == "SLD":
            self.cur_cash += ((quantity * price) - commission)

        if ticker not in self.positions:
            # self._add_position(
            #     action, ticker, quantity,
            #     price, commission
            # )
            position = Position(
                ticker, action, quantity,
                price, commission
            )
            self.positions[ticker] = position
        else:
            # self._modify_position(
            #     action, ticker, quantity,
            #     price, commission
            # )
            self.positions[ticker].transact_shares(
                action, quantity, price, commission
            )
        self.update_portfolio()

    def get_current_weights(self, ticker=None):
        #self.update_portfolio()
        wt = {}
        if ticker is None:
            for ticker in self.positions:
                pt = self.positions[ticker]
                wt[ticker] = pt.market_value / self.total_mkt_value
        else:
            pt = self.positions[ticker]
            wt = pt.market_value / self.total_mkt_value
        return wt
