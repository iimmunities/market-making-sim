# pnl_tracker.py

class PnLTracker:
    def __init__(self):
        self.cash = 0
        self.inventory = 0

    def buy(self, price, size):
        self.inventory += size
        self.cash -= price * size

    def sell(self, price, size):
        self.inventory -= size
        self.cash += price * size

    def total_pnl(self, fair_price):
        return self.cash + self.inventory * fair_price
