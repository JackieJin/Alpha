from enum import Enum


EventType = Enum("EventType", "TICK BAR SIGNAL ORDER FILL SENTIMENT TARGETWEIGHT TIME RECON SUGGESTEDORDER")

class Events(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    @property
    def typename(self):
        return self.type.name

    def __init__(self):
        self.pool = {}

    def get_event_type(self):
        return self.type

    def get(self, ticker):
        event = self.pool[ticker]
        return event

    def add(self, event):
        self.pool[event.ticker] = event.quantity


class TimeEvents(Events):
    def __init__(self, time):
        self.type = EventType.TIME
        self.time = time

class SignalEvents(Events):
    def __init__(self):
        self.type = EventType.SIGNAL


class SuggestedWeightEvents(Events):
    def __init__(self):
        self.type = EventType.TARGETWEIGHT


class SuggestedOrderEvents(Events):
    def __init__(self):
        self.type   = EventType.ORDER


class FillEvents(Events):

    def __init__(self):
        self.type = EventType.FILL

class SentimentEvents(Events):
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
