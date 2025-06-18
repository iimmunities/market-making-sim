import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuration
FAIR_PRICE_START = 100.0
VOLATILITY = 0.5
SPREAD = 1.0
ORDER_SIZE = 1
LAMBDA = 5  # average number of orders per step
SIM_DURATION = 100
LATENCY = 0.1

# State
np.random.seed(42)
fair_prices = [FAIR_PRICE_START]
inventory = 0
cash = 0
trade_log = []

# Simulation loop
for t in range(SIM_DURATION):
    fair_price = fair_prices[-1] + np.random.normal(0, VOLATILITY)
    fair_prices.append(fair_price)

    bid = fair_price - SPREAD / 2
    ask = fair_price + SPREAD / 2

    n_orders = np.random.poisson(LAMBDA)
    for _ in range(n_orders):
        side = np.random.choice(['buy', 'sell'])
        if side == 'buy' and np.random.rand() < 0.5:
            inventory -= ORDER_SIZE
            cash += ask * ORDER_SIZE
            trade_log.append((t, 'sell', ask))
        elif side == 'sell' and np.random.rand() < 0.5:
            inventory += ORDER_SIZE
            cash -= bid * ORDER_SIZE
            trade_log.append((t, 'buy', bid))

# Final P&L
final_fair_price = fair_prices[-1]
inventory_value = inventory * final_fair_price
total_pnl = cash + inventory_value

# Results
print(f"Final Cash: ${cash:.2f}")
print(f"Final Inventory: {inventory}")
print(f"Inventory Value: ${inventory_value:.2f}")
print(f"Total P&L: ${total_pnl:.2f}")

# Trade log
trade_df = pd.DataFrame(trade_log, columns=["time", "side", "price"])
plt.figure(figsize=(12, 6))
plt.plot(fair_prices, label='Fair Price')
plt.scatter(trade_df["time"], trade_df["price"], c=(trade_df["side"] == 'buy'), cmap='bwr', label='Trades', alpha=0.6)
plt.title("Market Making Simulation")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
