from core.event import EventType, FillEvent


class SimulationExecutionHandler(object):
    """
    The simulated execution handler for Interactive Brokers
    converts all order objects into their equivalent fill
    objects automatically without latency, slippage or
    fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def initialize(self, portfolio_handler):
        self.portfolio_handler = portfolio_handler

    def calculate_commission(self, quantity, fill_price):
        """
        Calculate the Interactive Brokers commission for
        a transaction. This is based on the US Fixed pricing,
        the details of which can be found here:
        https://www.interactivebrokers.co.uk/en/index.php?f=1590&p=stocks1
        """
        commission = min(
            0.5 * fill_price * quantity,
            max(1.0, 0.005 * quantity)
        )
        return commission

    def execute_order(self, order_events):
        """
        Converts OrderEvents into FillEvents "naively",
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - An Event object with order information.
        """
        if order_events.type == EventType.ORDER:
            order_events.type = EventType.FILL

        for ticker in order_events.pool:
            close_price = self.portfolio_handler.get_last_close(ticker)
            order_events.pool[ticker] = self._convert_suggested_to_fill(order_events.pool[ticker], close_price)
        return order_events

    def _convert_suggested_to_fill(self, order_event, price):
            ticker = order_event.ticker
            action   = order_event.action
            quantity = order_event.quantity
            fill_event = FillEvent(ticker, action, quantity, price)
            return fill_event