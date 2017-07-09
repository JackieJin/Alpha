from enum import Enum

EventType = Enum("EventType", "TICK BAR SIGNAL ORDER FILL SENTIMENT TARGETWEIGHT TIME RECON")

class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    @property
    def typename(self):
        return self.type.name



class TimeEvent(Event):
    def __init__(self,time):
        self.time = time
        self.type = EventType.TIME

class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, ticker, action, suggested_quantity=None):
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
        self.type = EventType.SIGNAL
        self.ticker = ticker
        self.action = action
        self.suggested_quantity = suggested_quantity


class TargetWeightEvent(Event):
    def __init__(self, ticker, suggested_weight = None):
        self.type   = EventType.TARGETWEIGHT
        self.ticker = ticker
        self.suggested_weight = suggested_weight

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. GOOG), action (BOT or SLD)
    and quantity.
    """
    def __init__(self, ticker, action, quantity):
        """
        Initialises the OrderEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The quantity of shares to transact.
        """
        self.type = EventType.ORDER
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
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """

    def __init__(
        self, timestamp, ticker,
        action, quantity,
        exchange, price,
        commission
    ):
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
        self.type = EventType.FILL
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.exchange = exchange
        self.price = price
        self.commission = commission


class SentimentEvent(Event):
    """
    Handles the event of streaming a "Sentiment" value associated
    with a ticker. Can be used for a generic "date-ticker-sentiment"
    service, often provided by many data vendors.
    """
    def __init__(self, timestamp, ticker, sentiment):
        """
        Initialises the SentimentEvent.

        Parameters:
        timestamp - The timestamp when the sentiment was generated.
        ticker - The ticker symbol, e.g. 'GOOG'.
        sentiment - A string, float or integer value of "sentiment",
            e.g. "bullish", -1, 5.4, etc.
        """
        self.type = EventType.SENTIMENT
        self.timestamp = timestamp
        self.ticker = ticker
        self.sentiment = sentiment
