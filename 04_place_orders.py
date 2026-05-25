"""
Example 4 — Authenticated Trading
Place a limit order, inspect open orders, cancel.
Requires .env with POLYMARKET_PRIVATE_KEY, POLYMARKET_FUNDER, POLYMARKET_SIGNATURE_TYPE.
"""
from src.client import get_authenticated_client
from src.market_discovery import get_market_by_slug
from src.trading import place_limit_order, cancel_order, get_open_orders
from src.portfolio import get_portfolio_summary

client = get_authenticated_client()
WALLET = "0xYourWalletHere"

# Portfolio snapshot
summary = get_portfolio_summary(client, WALLET)
print(f"Cash: ${summary.cash_usdc:.2f}  Positions: ${summary.positions_value:.2f}  Total: ${summary.total_value:.2f}")

# Place a low-ball limit order
markets = get_market_by_slug("how-many-fed-rate-cuts-in-2026")
yes_token = markets[2].yes_token_id

order_id = place_limit_order(client, token_id=yes_token, price=0.05, size=5.0, side="BUY")
print(f"Placed order: {order_id}")

# Inspect open orders
open_orders = get_open_orders(client)
for o in open_orders[:3]:
    print(f"  {o['side']} {o['original_size']} @ {o['price']}  id={o['id'][:10]}...")

# Cancel it
if order_id:
    cancel_order(client, order_id)
    print("Order cancelled.")
