from math import floor

from event import EventType
from qstrader.order.suggested import SuggestedOrder

class LiquidateRebalancePositionSizer(object):
    """
    Carries out a periodic full liquidation and rebalance of
    the Portfolio.

    This is achieved by determining whether an order type type
    is "EXIT" or "BOT/SLD".

    If the former, the current quantity of shares in the ticker
    is determined and then BOT or SLD to net the position to zero.

    If the latter, the current quantity of shares to obtain is
    determined by prespecified weights and adjusted to reflect
    current account equity.
    """
    def __init__(self, ticker_weights):
        self.ticker_weights = ticker_weights

    def size_order(self, portfolio, initial_order):
        """
        Size the order to reflect the dollar-weighting of the
        current equity account size based on pre-specified
        ticker weights.
        """
        ticker = initial_order.ticker
        if initial_order.action == "EXIT":
            # Obtain current quantity and liquidate
            cur_quantity = portfolio.positions[ticker].quantity
            if cur_quantity > 0:
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity
            else:
                initial_order.action = "BOT"
                initial_order.quantity = cur_quantity
        else:
            weight = self.ticker_weights[ticker]
            # Determine total portfolio value, work out dollar weight
            # and finally determine integer quantity of shares to purchase
            price = portfolio.price_handler.tickers[ticker]["adj_close"]
            price = PriceParser.display(price)
            equity = PriceParser.display(portfolio.equity)
            dollar_weight = weight * equity
            weighted_quantity = int(floor(dollar_weight / price))
            initial_order.quantity = weighted_quantity
        return initial_order




class ConstantPositionSizer(object):
    """
    Size the order to reflect the dollar-weighting of the
    current equity account size based on pre-specified
    ticker weights.
    """
    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def size_order(self, target_weight_event):
        initial_order = []
        if target_weight_event.type == EventType.TARGETWEIGHT:
            current_weights      = self.portfolio_handler.get_current_weights()
            suggested_weights    = target_weight_event.suggested_weights

            for ticker in suggested_weights:
                if ticker in current_weights:
                    changed_weight      = suggested_weights[ticker] - current_weights[ticker]
                    quantity            = self._get_quantity_from_weight(ticker, changed_weight)
                    if quantity > 0:
                        action = "BOT"
                    else:
                        action = "SLD"
                        quantity = - quantity
                    order = SuggestedOrder(ticker, action, quantity)
                    initial_order.append(order)
            return initial_order
        else:
            raise NotImplemented("Unsupported event.type '%s' in size_order" % target_weight_event.type)


    def _get_quantity_from_weight(self, ticker, weight):
        price = self.portfolio_handler.price_handler.tickers[ticker]["adj_close"]
        equity = self.portfolio_handler.portfolio.equity
        dollar_weight = weight * equity
        weighted_quantity = int(floor(dollar_weight / price))
        quantity = weighted_quantity
        return quantity
