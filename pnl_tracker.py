class PnLTracker:
    def __init__(self):
        self.inventory = 0
        self.cash = 0.0

    def buy(self, price, size):
        self.inventory += size
        self.cash -= price * size

    def sell(self, price, size):
        self.inventory -= size
        self.cash += price * size

    def total_pnl(self, current_price):
        return self.cash + self.inventory * current_price
