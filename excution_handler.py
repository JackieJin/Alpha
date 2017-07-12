from events import EventType, FillEvents
from suggested import FilledOrder

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

    def __init__(self, events_queue):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.

        Parameters:
        events_queue - The Queue of Event objects.
        """
        self.events_queue = events_queue

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

    def execute_order(self, suggested_orders):
        """
        Converts OrderEvents into FillEvents "naively",
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - An Event object with order information.
        """
        if suggested_orders.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            filled_orders = FillEvents()
            for ticker in suggested_orders.pool:
                order  = self.portfolio_handler.get_last_timestamp(suggested_orders.pool[ticker])
                timestamp = order.time
                ticker = order.ticker
                action = order.action
                quantity = order.quantity

                # Obtain the fill price
                # if self.portfolio_handler.istick():
                #     bid, ask = self.portfolio_handler.get_best_bid_ask(ticker)
                #     if event.action == "BOT":
                #         fill_price = ask
                #     else:
                #         fill_price = bid
                # else:
                close_price = self.portfolio_handler.get_last_close(ticker)
                fill_price = close_price

                # Set a dummy exchange and calculate trade commission
                exchange = "ARCA"
                commission = self.calculate_commission(quantity, fill_price)

                # Create the FillEvent and place on the events queue
                fill_order = FilledOrder(
                    timestamp, ticker,
                    action, quantity,
                    exchange, fill_price,
                    commission
                )
                filled_orders.add(fill_order)
            self.events_queue.put(filled_orders)

            if self.compliance is not None:
                self.compliance.record_trade(filled_orders)
