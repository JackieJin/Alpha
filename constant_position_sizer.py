from math import floor
from core.event import EventType, OrderEvent
from core.pool import OrderEventPool


class ConstantPositionSizer(object):
    """
    Size the order to reflect the dollar-weighting of the
    current equity account size based on pre-specified
    ticker weights.
    """
    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def size_order(self, weight_events):
        initial_order_events = OrderEventPool(weight_events.time)
        initial_order_events.type = EventType.ORDER
        if weight_events.type == EventType.TARGETWEIGHT:
            current_weights      = self.portfolio_handler.get_current_weights()
            suggested_weights    = weight_events.get_weights()

            for ticker in suggested_weights:
                if ticker in current_weights:
                    changed_weight = suggested_weights[ticker] - current_weights[ticker]
                else:
                    changed_weight = suggested_weights[ticker]

                quantity = self._get_quantity_from_weight(ticker, changed_weight)
                if quantity is not None:
                    if quantity > 0:
                        action = "BOT"
                    else:
                        action = "SLD"
                        quantity = - quantity
                else:
                     action = None

                order = OrderEvent(ticker, action, quantity)
                initial_order_events.add(order)
            initial_order_events.print_orders()
            return initial_order_events
        else:
            raise NotImplemented("Unsupported event.type '%s' in size_order" % weight_events.type)


    def _get_quantity_from_weight(self, ticker, weight):
        price = self.portfolio_handler.get_last_close(ticker)
        equity = self.portfolio_handler.portfolio.equity
        dollar_weight = weight * equity
        if price is not None:
            weighted_quantity = int(floor(dollar_weight / price))
        else:
            weighted_quantity = None
        quantity = weighted_quantity
        return quantity
