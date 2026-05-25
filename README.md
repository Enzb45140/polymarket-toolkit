# Polymarket Toolkit

A Python toolkit for programmatic trading and analysis on [Polymarket](https://polymarket.com), a decentralised prediction market platform built on Polygon.

## Features

- **Market discovery** — search and filter active markets via Gamma metadata API, ranked by volume
- **Orderbook analysis** — L1/L2 snapshot and microstructure metrics (spread, depth, notional imbalance)
- **WebSocket streaming** — real-time orderbook updates with local state management
- **Authenticated trading** — limit and market order placement, cancellation, killswitch
- **Portfolio tracking** — live positions, cash balance, mark-to-market P&L, trade history

## Stack

```
Python 3.10+
py-clob-client     # Polymarket CLOB REST + order signing
websockets         # Real-time market data streaming
pandas / numpy     # Data wrangling
python-dotenv      # Credential management
matplotlib         # Orderbook visualisation
```

## Setup

```bash
git clone https://github.com/yourusername/polymarket-toolkit
cd polymarket-toolkit
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
```

### `.env` credentials

```
POLYMARKET_PRIVATE_KEY=0x...
POLYMARKET_FUNDER=0x...
POLYMARKET_SIGNATURE_TYPE=1   # 0=EOA, 1=Magic, 2=proxy
```

> Signature type depends on how your wallet was created. Magic/email wallets use type 1.

## Usage

### Market discovery

```python
from src.market_discovery import search_markets

# Find top election markets by volume
markets = search_markets("election", max_pages=4, top_n=10)
print(markets[["question", "gamma_volume"]].to_string())
```

### Orderbook snapshot

```python
from src.orderbook import get_orderbook_stats, print_ladder

stats = get_orderbook_stats(yes_token_id, top_n=5)
print(f"mid={stats.mid:.4f}  spread={stats.spread:.4f}  bid_depth={stats.bid_depth_top_n:.0f}")
print_ladder(yes_token_id, max_levels=10)
```

### Place & cancel orders

```python
from src.trading import place_limit_order, cancel_order

order_id = place_limit_order(client, token_id=yes_token_id, price=0.14, size=50, side="BUY")
cancel_order(client, order_id)
```

### Portfolio snapshot

```python
from src.portfolio import get_portfolio_summary

summary = get_portfolio_summary(client, wallet_address)
print(summary)
```

## Project structure

```
polymarket-toolkit/
├── src/
│   ├── client.py            # Client initialisation (read-only + authenticated)
│   ├── market_discovery.py  # Market search, filtering, volume ranking
│   ├── orderbook.py         # L2 snapshot, microstructure metrics, visualisation
│   ├── streaming.py         # WebSocket listener with local book state
│   ├── trading.py           # Order placement, cancellation, killswitch
│   ├── portfolio.py         # Positions, cash balance, trade history
│   └── utils.py             # Shared helpers (token parsing, formatting)
├── examples/
│   ├── 01_market_discovery.py
│   ├── 02_orderbook_analysis.py
│   ├── 03_stream_live_data.py
│   └── 04_place_orders.py
├── .env.example
├── requirements.txt
└── README.md
```

## Disclaimer

For educational and research purposes only. Validate all inputs before live trading. Be aware of georestrictions.
