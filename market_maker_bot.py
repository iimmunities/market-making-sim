# market_maker_bot.py

class MarketMakerBot:
    def __init__(self, spread, skew_factor=0.0):
        self.spread = spread
        self.skew_factor = skew_factor

    def get_quotes(self, fair_price, inventory):
        skew = self.skew_factor * inventory
        bid = fair_price - self.spread / 2 + skew
        ask = fair_price + self.spread / 2 + skew
        return bid, ask
