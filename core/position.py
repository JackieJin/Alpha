

class Position(object):
    def __init__(
        self,  ticker, init_action=None, init_quantity=0,
        init_price=0, init_commission=0,
        bid=None, ask=None
    ):
        """
        Set up the initial "account" of the Position to be
        zero for most items, with the exception of the initial
        purchase/sale.

        Then calculate the initial values and finally update the
        market value of the transaction.
        """
        
        self.ticker         = ticker
        self.realised_pnl   = 0
        self.market_value   = 0
        self.cost_basis     = 0
        self.unrealised_pnl = 0
        self.total_pnl      = 0

        self.buys           = 0
        self.sells          = 0
        self.net            = 0

        self.avg_bot        = 0
        self.avg_sld        = 0
        self.avg_price      = 0

        self.total_bot      = 0
        self.total_sld      = 0
        self.total_commission = 0
        self.net_total      = 0
        self.net_incl_comm  = 0

        self.transact_shares(init_action, init_quantity, init_price, init_commission, bid, ask)


    def update_market_value(self, bid, ask):
        """
        The market value is tricky to calculate as we only have
        access to the top of the order book through Interactive
        Brokers, which means that the true redemption price is
        unknown until executed.

        However, it can be estimated via the mid-price of the
        bid-ask spread. Once the market value is calculated it
        allows calculation of the unrealised and realised profit
        and loss of any transactions.
        """
        midpoint = (bid + ask) / 2

        self.market_value   = self.net * midpoint
        self.unrealised_pnl = self.market_value - self.cost_basis
        self.total_pnl      = self.unrealised_pnl + self.realised_pnl

    def transact_shares(self, action, quantity, price, commission, bid=None, ask=None):
        """
        Calculates the adjustments to the Position that occur
        once new shares are bought and sold.

        Takes care to update the average bought/sold, total
        bought/sold, the cost basis and PnL calculations,
        as carried out through Interactive Brokers TWS.
        """
        if bid is None: 
            bid = price
        if ask is None:
            ask = price

        if action is None:
            return

        self.total_commission += commission

        # Adjust total bought and sold
        if action == "BOT":
            self.avg_bot     = (self.avg_bot * self.buys + price * quantity) / (self.buys + quantity)

            if self.net < 0:
                self.realised_pnl += min(quantity, abs(self.net)) * (self.avg_price - price) - commission  # Adjust realised PNL
                commission        = 0      # assume commission is all in realised_pnl
            # Increasing long position
            self.avg_price  = (self.avg_price * self.net + price * quantity + commission) / (self.net + quantity)
            self.buys       += quantity
            self.total_bot  = self.buys * self.avg_bot

        # action == "SLD"
        else:
            self.avg_sld    = (self.avg_sld * self.sells + price * quantity) / (self.sells + quantity)

            if self.net > 0:
                self.realised_pnl += min(quantity, abs(self.net)) * (price - self.avg_price) - commission  # Adjust realised PNL
                commission        = 0  # assume commission is all in realised_pnl

            self.avg_price  = (self.avg_price * self.net - price * quantity - commission) / (self.net - quantity)
            self.sells      += quantity
            self.total_sld  = self.sells * self.avg_sld

        # Adjust net values, including commissions
        self.net            = self.buys - self.sells
        self.net_total      = self.total_sld - self.total_bot
        self.net_incl_comm  = self.net_total - self.total_commission
        self.cost_basis     = self.net * self.avg_price

        self.update_market_value(bid, ask)

if __name__ == "__main__":
    p = Position('AAPL', 'BOT', 150, 100, 5, 150, 150)
    print(vars(p))
    p.transact_shares('SLD', 200, 105, 5)
    print(vars(p))