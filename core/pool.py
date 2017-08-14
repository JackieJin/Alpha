from core.event import EventType, WeightEvent


class EventPool(object):
    @property
    def typename(self):
        return self.type.name

    def __init__(self, time):
        self.pool = {}
        self.type = EventType.TIME
        self.time = time

    def get(self, ticker):
        event = self.pool[ticker]
        return event

    def add(self, event):
        self.pool[event.ticker] = event

class PriceEventPool(EventPool):
    def __init__(self, time):
        EventPool.__init__(self,time)
        self.type = EventType.PRICE


class WeightEventPool(EventPool):
    def __init__(self, time):
        EventPool.__init__(self,time)
        self.type = EventType.TARGETWEIGHT

    def get_weights(self):
        weights = {key: value.weight for key, value in self.pool.items()}
        return weights

    def add_weights(self, tickers_and_weights):
        for ticker in tickers_and_weights:
            weight_event = WeightEvent(ticker, tickers_and_weights[ticker])
            self.pool[ticker] = weight_event


class OrderEventPool(EventPool):
    def __init__(self, time):
        EventPool.__init__(self, time)
        self.type = EventType.ORDER


    def print_orders(self):
        print("Time: %s " % self.time)
        for ticker in self.pool:
            self.pool[ticker].print_order()