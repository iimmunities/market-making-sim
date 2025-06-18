# main.py
from performance_metrics import sharpe_ratio, sortino_ratio, max_drawdown, realized_unrealized_pnl
from market_maker_bot import MarketMakerBot
from order_flow import generate_orders
from pnl_tracker import PnLTracker
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import json

# Load config from file
with open("config.json") as f:
    config = json.load(f)

FAIR_PRICE_START = config["FAIR_PRICE_START"]
VOLATILITY = config["VOLATILITY"]
BASE_SPREAD = config["BASE_SPREAD"]
ORDER_SIZE = config["ORDER_SIZE"]
LAMBDA = config["LAMBDA"]
SIM_DURATION = config["SIM_DURATION"]
ROLLING_WINDOW = config["ROLLING_WINDOW"]
np.random.seed(config["RANDOM_SEED"])

# Initialize
fair_prices = [FAIR_PRICE_START]

# Define bots
bots = [
    {
        "bot": MarketMakerBot(name="StaticBot", spread=BASE_SPREAD, skew_factor=0.0),
        "pnl": PnLTracker(),
        "trades": [],
        "pnl_over_time": [],
        "inventory_over_time": []
    },
    {
        "bot": MarketMakerBot(name="SkewBot", spread=BASE_SPREAD, skew_factor=0.05),
        "pnl": PnLTracker(),
        "trades": [],
        "pnl_over_time": [],
        "inventory_over_time": []
    },
    {
        "bot": MarketMakerBot(name="VolAwareBot", spread=BASE_SPREAD, skew_factor=0.03),
        "pnl": PnLTracker(),
        "trades": [],
        "pnl_over_time": [],
        "inventory_over_time": []
    }
]

# Simulation loop
for t in range(SIM_DURATION):
    # Update fair price
    fair_price = fair_prices[-1] + np.random.normal(0, VOLATILITY)
    fair_prices.append(fair_price)

    # Estimate volatility
    recent_returns = np.diff(fair_prices[-ROLLING_WINDOW:])
    vol_estimate = np.std(recent_returns) if len(recent_returns) > 0 else 0

    # Generate market orders
    orders = generate_orders(LAMBDA)

    # Let each bot quote and fill
    for entry in bots:
        bot = entry["bot"]
        pnl = entry["pnl"]
        log = entry["trades"]

        # Vol-aware bot adapts spread
        spread = BASE_SPREAD + (0.5 * vol_estimate if bot.name == "VolAwareBot" else 0)
        bid, ask = bot.get_quotes(fair_price, pnl.inventory, vol_estimate)

        for side in orders:
            if side == 'buy' and np.random.rand() < 0.5:
                pnl.sell(ask, ORDER_SIZE)
                log.append((t, 'sell', ask))
            elif side == 'sell' and np.random.rand() < 0.5:
                pnl.buy(bid, ORDER_SIZE)
                log.append((t, 'buy', bid))

        entry["pnl_over_time"].append(pnl.total_pnl(fair_price))
        entry["inventory_over_time"].append(pnl.inventory)

# Plot price and trades for each bot
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))
plt.plot(fair_prices, label='Fair Price', linewidth=2)

colors = ['cyan', 'magenta', 'yellow']
for i, entry in enumerate(bots):
    trade_df = pd.DataFrame(entry["trades"], columns=["time", "side", "price"])
    c = colors[i % len(colors)]
    plt.scatter(trade_df["time"], trade_df["price"],
                label=entry["bot"].name, alpha=0.6, c=c, s=20)
plt.title("Market Making Simulation: Multi-Bot")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot P&L and Inventory Over Time
plt.figure(figsize=(12, 6))
for i, entry in enumerate(bots):
    plt.plot(entry["pnl_over_time"], label=f"{entry['bot'].name} P&L")
plt.title("P&L Over Time")
plt.xlabel("Time Step")
plt.ylabel("Total P&L")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
for i, entry in enumerate(bots):
    plt.plot(entry["inventory_over_time"], label=f"{entry['bot'].name} Inventory")
plt.title("Inventory Over Time")
plt.xlabel("Time Step")
plt.ylabel("Inventory")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Export trade logs to CSV
os.makedirs("logs", exist_ok=True)
for entry in bots:
    trade_df = pd.DataFrame(entry["trades"], columns=["time", "side", "price"])
    trade_df.to_csv(f"logs/{entry['bot'].name}_trades.csv", index=False)

# Print summary
for entry in bots:
    bot = entry["bot"]
    pnl = entry["pnl"]
    final_price = fair_prices[-1]
    print(f"{bot.name} -> Cash: {pnl.cash:.2f}, Inventory: {pnl.inventory}, "
          f"Inventory Value: {pnl.inventory * final_price:.2f}, "
          f"Total P&L: {pnl.total_pnl(final_price):.2f}")

# Leaderboard
print("\n🏆 Final Ranking by Total P&L:")
sorted_bots = sorted(bots, key=lambda e: e["pnl"].total_pnl(fair_prices[-1]), reverse=True)
for rank, entry in enumerate(sorted_bots, start=1):
    bot = entry["bot"]
    pnl = entry["pnl"].total_pnl(fair_prices[-1])
    print(f"{rank}. {bot.name}: ${pnl:.2f}")

# Summary + Leaderboard
print("\n📈 Bot Performance Summary")
for entry in bots:
    bot = entry["bot"]
    pnl = entry["pnl"]
    final_price = fair_prices[-1]
    total_pnl = pnl.total_pnl(final_price)
    print(f"{bot.name:<12} | Cash: ${pnl.cash:8.2f} | Inventory: {pnl.inventory:3} | "
          f"Value: ${pnl.inventory * final_price:8.2f} | Total P&L: ${total_pnl:8.2f}")

# Leaderboard
print("\n🏆 Final Ranking by Total P&L:")
sorted_bots = sorted(bots, key=lambda e: e["pnl"].total_pnl(fair_prices[-1]), reverse=True)
medals = ['🥇', '🥈', '🥉']
for rank, entry in enumerate(sorted_bots, start=1):
    bot = entry["bot"]
    pnl = entry["pnl"].total_pnl(fair_prices[-1])
    icon = medals[rank - 1] if rank <= 3 else f"{rank}."
    print(f"{icon} {bot.name:<12} | P&L: ${pnl:.2f}")

# Bar chart of final P&L
bot_names = [entry["bot"].name for entry in bots]
final_pnls = [entry["pnl"].total_pnl(fair_prices[-1]) for entry in bots]

plt.figure(figsize=(10, 5))
bars = plt.barh(bot_names, final_pnls, color='skyblue')
plt.xlabel("Total P&L")
plt.title("💰 Bot P&L Comparison")
plt.grid(True, axis='x')

# Add value labels on bars
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
             f"${bar.get_width():.2f}", va='center')

plt.tight_layout()
plt.show()

# Extended performance metrics
print("\n📊 Performance Metrics:")
for entry in bots:
    bot = entry["bot"]
    pnl = entry["pnl"]
    series = entry["pnl_over_time"]
    final_price = fair_prices[-1]

    sharpe = sharpe_ratio(series)
    sortino = sortino_ratio(series)
    mdd = max_drawdown(series)
    realized, unrealized = realized_unrealized_pnl(pnl.cash, pnl.inventory, final_price)

    print(f"{bot.name:<12} | Sharpe: {sharpe:.2f} | Sortino: {sortino:.2f} | "
          f"Max DD: ${mdd:.2f} | Realized: ${realized:.2f} | Unrealized: ${unrealized:.2f}")

