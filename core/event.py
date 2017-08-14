from enum import Enum

EventType = Enum("EventType", "PRICE TICK BAR SIGNAL ORDER FILL SENTIMENT TARGETWEIGHT TIME RECON")

class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    # @property
    # def ticker(self):
    #     return self.ticker



# class SignalEvent(Event):
#     """
#     Handles the event of sending a Signal from a Strategy object.
#     This is received by a Portfolio object and acted upon.
#     """
#     def __init__(self, ticker, action, suggested_quantity=None):
#         """
#         Initialises the SignalEvent.
#
#         Parameters:
#         ticker - The ticker symbol, e.g. 'GOOG'.
#         action - 'BOT' (for long) or 'SLD' (for short).
#         suggested_quantity - Optional positively valued integer
#             representing a suggested absolute quantity of units
#             of an asset to transact in, which is used by the
#             PositionSizer and RiskManager.
#         """
#         self.ticker = ticker
#         self.action = action
#         self.suggested_quantity = suggested_quantity

class PriceEvent(Event):
    def __init__(self, ticker, price, adj_price):
        self.ticker      = ticker
        self.price       = price
        self.adj_price   = adj_price

class WeightEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, ticker, weight=0):
        """
        Initialises the SignalEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        suggested_quantity - Optional positively valued integer
            representing a suggested absolute quantity of units
            of an asset to transact in, which is used by the
            PositionSizer and RiskManager.
        """
        self.ticker = ticker
        self.weight = weight


class OrderEvent(Event):

    def __init__(self, ticker, action, quantity):
        """
        Initialises the OrderEvent.
        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The quantity of shares to transact.
        """
        self.ticker = ticker
        self.action = action
        self.quantity = quantity

    def print_order(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(
            "Order: Ticker=%s, Action=%s, Quantity=%s" % (
                self.ticker, self.action, self.quantity
            )
        )

class FillEvent(Event):

    def __init__(self, ticker, action, quantity, price):
        """
        Initialises the FillEvent object.
        timestamp - The timestamp when the order was filled.
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The filled quantity.
        exchange - The exchange where the order was filled.
        price - The price at which the trade was filled
        commission - The brokerage commission for carrying out the trade.
        """
        self.ticker   = ticker
        self.action   = action
        self.quantity = quantity
        self.price    = price

    def isvalid(self):
        flag = True
        if self.action is None or self.quantity is None:
            flag = False

        return flag

if __name__ == "__main__":
    event = WeightEvent('AAPL',10.0)
