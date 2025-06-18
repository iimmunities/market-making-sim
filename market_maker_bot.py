class MarketMakerBot:
    def __init__(self, name, spread=1.0, skew_factor=0.0):
        self.name = name
        self.spread = spread
        self.skew_factor = skew_factor

    def get_quotes(self, fair_price, inventory, vol_estimate=0):
        skew = self.skew_factor * inventory
        dynamic_spread = self.spread + (0.5 * vol_estimate if self.name == "VolAwareBot" else 0)
        bid = fair_price - dynamic_spread / 2 + skew
        ask = fair_price + dynamic_spread / 2 + skew
        return bid, ask
