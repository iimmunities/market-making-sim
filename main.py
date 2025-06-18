# main.py

from market_maker_bot import MarketMakerBot
from order_flow import generate_orders
from pnl_tracker import PnLTracker
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Config
FAIR_PRICE_START = 100.0
VOLATILITY = 0.5
SPREAD = 1.0
ORDER_SIZE = 1
LAMBDA = 5
SIM_DURATION = 100
np.random.seed(42)

# Initialize
fair_prices = [FAIR_PRICE_START]
trade_log = []
bot = MarketMakerBot(spread=SPREAD, skew_factor=0.05)
pnl = PnLTracker()

# Simulation loop
for t in range(SIM_DURATION):
    # Update fair price using Gaussian noise
    fair_price = fair_prices[-1] + np.random.normal(0, VOLATILITY)
    fair_prices.append(fair_price)

    # Get bot's bid/ask with inventory-based skew
    bid, ask = bot.get_quotes(fair_price, pnl.inventory)

    # Generate trader order flow
    orders = generate_orders(LAMBDA)

    for side in orders:
        if side == 'buy' and np.random.rand() < 0.5:
            pnl.sell(ask, ORDER_SIZE)
            trade_log.append((t, 'sell', ask))
        elif side == 'sell' and np.random.rand() < 0.5:
            pnl.buy(bid, ORDER_SIZE)
            trade_log.append((t, 'buy', bid))

# Create trade DataFrame
trade_df = pd.DataFrame(trade_log, columns=["time", "side", "price"])

# Plot results
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))
plt.plot(fair_prices, label='Fair Price')
plt.scatter(
    trade_df["time"], 
    trade_df["price"], 
    c=(trade_df["side"] == 'buy'), 
    cmap='bwr', 
    alpha=0.6, 
    label='Trades'
)
plt.title("Market Making Simulation")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Print final performance
print("Final Cash:", round(pnl.cash, 2))
print("Final Inventory:", pnl.inventory)
print("Inventory Value:", round(pnl.inventory * fair_prices[-1], 2))
print("Total P&L:", round(pnl.total_pnl(fair_prices[-1]), 2))
