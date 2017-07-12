from math import floor

from events import EventType, SuggestedOrderEvents
from qstrader.order.suggested import SuggestedOrder



class ConstantPositionSizer(object):
    """
    Size the order to reflect the dollar-weighting of the
    current equity account size based on pre-specified
    ticker weights.
    """
    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def size_order(self, target_weight_events):
        initial_order = SuggestedOrderEvents()

        if target_weight_events.type == EventType.TARGETWEIGHT:
            current_weights      = self.portfolio_handler.get_current_weights()
            suggested_weights    = {ticker: suggested_weight.quantity for (ticker, suggested_weight) in target_weight_events.pool.items()}

            for ticker in suggested_weights:
                if ticker in current_weights:
                    changed_weight = suggested_weights[ticker] - current_weights[ticker]
                    quantity = self._get_quantity_from_weight(ticker, changed_weight)
                    if quantity > 0:
                        action = "BOT"
                    else:
                        action = "SLD"
                        quantity = - quantity
                    order = SuggestedOrder(ticker, action, quantity)
                    initial_order.add(order)
            return initial_order
        else:
            raise NotImplemented("Unsupported event.type '%s' in size_order" % target_weight_events.type)


    def _get_quantity_from_weight(self, ticker, weight):
        price = self.portfolio_handler.price_handler.tickers[ticker]["adj_close"]
        equity = self.portfolio_handler.portfolio.equity
        dollar_weight = weight * equity
        weighted_quantity = int(floor(dollar_weight / price))
        quantity = weighted_quantity
        return quantity
