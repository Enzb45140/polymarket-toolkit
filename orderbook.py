import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from py_clob_client.client import ClobClient
from src.client import get_readonly_client


@dataclass
class OrderbookStats:
    best_bid: float
    best_ask: float
    mid: float
    spread: float
    bid_depth_top_n: float
    ask_depth_top_n: float
    bid_notional_top_n: float
    ask_notional_top_n: float
    imbalance: float


def _to_df(levels: list, side: str) -> pd.DataFrame:
    rows = [{"price": float(l.price), "size": float(l.size)} for l in levels]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("price", ascending=(side == "asks")).reset_index(drop=True)
    df["notional"] = df["price"] * df["size"]
    df["cum_size"] = df["size"].cumsum()
    df["cum_notional"] = df["notional"].cumsum()
    return df


def get_orderbook_stats(token_id: str, top_n: int = 5, client: ClobClient = None) -> OrderbookStats:
    if client is None:
        client = get_readonly_client()

    ob = client.get_order_book(token_id)
    bids = _to_df(ob.bids, "bids")
    asks = _to_df(ob.asks, "asks")

    best_bid = bids["price"].iloc[0] if not bids.empty else 0.0
    best_ask = asks["price"].iloc[0] if not asks.empty else 1.0
    mid = (best_bid + best_ask) / 2
    spread = best_ask - best_bid

    bid_depth = bids["size"].iloc[:top_n].sum() if not bids.empty else 0.0
    ask_depth = asks["size"].iloc[:top_n].sum() if not asks.empty else 0.0
    bid_notional = bids["notional"].iloc[:top_n].sum() if not bids.empty else 0.0
    ask_notional = asks["notional"].iloc[:top_n].sum() if not asks.empty else 0.0

    total = bid_depth + ask_depth
    imbalance = (bid_depth - ask_depth) / total if total > 0 else 0.0

    return OrderbookStats(
        best_bid=best_bid,
        best_ask=best_ask,
        mid=mid,
        spread=spread,
        bid_depth_top_n=bid_depth,
        ask_depth_top_n=ask_depth,
        bid_notional_top_n=bid_notional,
        ask_notional_top_n=ask_notional,
        imbalance=imbalance,
    )


def get_orderbook_df(token_id: str, side: str, max_levels: int = 20, client: ClobClient = None) -> pd.DataFrame:
    if client is None:
        client = get_readonly_client()
    ob = client.get_order_book(token_id)
    levels = ob.bids if side == "bids" else ob.asks
    return _to_df(levels, side).head(max_levels)


def print_ladder(token_id: str, max_levels: int = 10, label: str = "", client: ClobClient = None):
    if client is None:
        client = get_readonly_client()
    ob = client.get_order_book(token_id)
    bids = _to_df(ob.bids, "bids")
    asks = _to_df(ob.asks, "asks")
    mid = (bids["price"].iloc[0] + asks["price"].iloc[0]) / 2 if not bids.empty and not asks.empty else 0

    print(f"\nORDER BOOK — {label or token_id[:12]}")
    print(f"{'ASK':>8}  {'PRICE':>8} | {'SIZE':>10}")
    print("-" * 42)
    for _, r in asks.iloc[:max_levels].iloc[::-1].iterrows():
        print(f"{'':>8}  {r['price']:>8.4f} | {r['size']:>10.2f}")
    print(f"{'':>8}  {'MID':>8.4f}  {mid:.4f}")
    print("-" * 42)
    for _, r in bids.iloc[:max_levels].iterrows():
        print(f"{r['size']:>8.2f}  {r['price']:>8.4f} |")


def plot_depth(token_id: str, max_levels: int = 30, title: str = "", client: ClobClient = None):
    if client is None:
        client = get_readonly_client()
    bids = get_orderbook_df(token_id, "bids", max_levels, client)
    asks = get_orderbook_df(token_id, "asks", max_levels, client)

    fig, ax = plt.subplots(figsize=(10, 5))
    if not bids.empty:
        ax.step(bids["price"], bids["cum_size"], where="post", color="#2196F3", label="Bids")
    if not asks.empty:
        ax.step(asks["price"], asks["cum_size"], where="post", color="#FF9800", label="Asks")

    ax.set_xlabel("Price")
    ax.set_ylabel("Cumulative Size")
    ax.set_title(title or "Orderbook Depth")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig
