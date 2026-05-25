"""
Example 1 — Market Discovery
Find top prediction markets by keyword and volume.
"""
from src.client import get_readonly_client
from src.market_discovery import search_markets, get_market_by_slug

client = get_readonly_client()

# Search by keyword
df = search_markets("Fed rate", client=client, max_pages=4, top_n=10)
print(df[["question", "gamma_volume"]].to_string())

# Or fetch directly from a known event slug
markets = get_market_by_slug("how-many-fed-rate-cuts-in-2026")
for m in markets[:5]:
    print(f"{m.question} | YES: {m.yes_token_id[:12]}...")
