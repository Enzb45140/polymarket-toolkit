"""
Example 3 — Live WebSocket Streaming
Subscribe to real-time orderbook updates for a market.
"""
from src.client import get_readonly_client
from src.market_discovery import get_market_by_slug
from src.streaming import run_stream, LocalOrderbook

client = get_readonly_client()
markets = get_market_by_slug("how-many-fed-rate-cuts-in-2026")
yes_token = markets[2].yes_token_id


def on_update(asset_id: str, book: LocalOrderbook):
    if book.mid:
        print(f"  bid={book.best_bid:.4f}  ask={book.best_ask:.4f}  mid={book.mid:.4f}  spread={book.spread:.4f}")


print(f"Streaming {yes_token[:16]}... (30s)")
run_stream([yes_token], on_update=on_update, duration_seconds=30)
