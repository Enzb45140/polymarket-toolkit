"""
Example 2 — Orderbook Analysis
Fetch L2 snapshot, print ladder, compute microstructure metrics.
"""
from src.client import get_readonly_client
from src.market_discovery import get_market_by_slug
from src.orderbook import get_orderbook_stats, print_ladder, plot_depth
import matplotlib.pyplot as plt

client = get_readonly_client()
markets = get_market_by_slug("how-many-fed-rate-cuts-in-2026")
market = markets[2]  # "Will 2 Fed rate cuts happen in 2026?"

yes_token = market.yes_token_id
stats = get_orderbook_stats(yes_token, top_n=5, client=client)

print(f"Market : {market.question}")
print(f"Mid    : {stats.mid:.4f}  Spread: {stats.spread:.4f}")
print(f"Bid depth (top 5): {stats.bid_depth_top_n:.0f}  Ask depth: {stats.ask_depth_top_n:.0f}")
print(f"Imbalance: {stats.imbalance:+.3f}  (positive = bid-heavy)")

print_ladder(yes_token, max_levels=10, label=market.question, client=client)

fig = plot_depth(yes_token, max_levels=30, title=f"Depth | {market.question[:50]}", client=client)
plt.show()
