import requests
import pandas as pd
from dataclasses import dataclass
from py_clob_client.client import ClobClient
import py_clob_client.clob_types as pm_types
from src.client import DATA_BASE


@dataclass
class PortfolioSummary:
    cash_usdc: float
    positions_value: float
    total_value: float
    n_positions: int


def get_cash_balance(client: ClobClient, signature_type: int = 1) -> float:
    params = pm_types.BalanceAllowanceParams(
        asset_type=pm_types.AssetType.COLLATERAL,
        signature_type=signature_type,
    )
    raw = client.get_balance_allowance(params)
    return float(raw.get("balance", 0)) / 1e6


def get_positions(wallet: str) -> pd.DataFrame:
    resp = requests.get(f"{DATA_BASE}/positions", params={"user": wallet}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return pd.DataFrame()

    rows = []
    for p in data:
        size = float(p.get("size", 0) or 0)
        avg_price = float(p.get("avgPrice", 0) or 0)
        current_price = float(p.get("currentPrice", 0) or 0)
        initial_value = size * avg_price
        current_value = size * current_price
        rows.append({
            "market": p.get("title", "")[:40],
            "outcome": p.get("outcome", ""),
            "side": p.get("side", ""),
            "size": size,
            "avg_price": avg_price,
            "current_price": current_price,
            "initial_value": initial_value,
            "current_value": current_value,
            "pnl": current_value - initial_value,
            "pnl_pct": (current_value / initial_value - 1) * 100 if initial_value > 0 else 0,
            "expiry": p.get("endDate", ""),
        })

    return pd.DataFrame(rows).sort_values("pnl")


def get_portfolio_summary(client: ClobClient, wallet: str, signature_type: int = 1) -> PortfolioSummary:
    cash = get_cash_balance(client, signature_type)
    positions = get_positions(wallet)
    pos_value = positions["current_value"].sum() if not positions.empty else 0.0

    return PortfolioSummary(
        cash_usdc=cash,
        positions_value=pos_value,
        total_value=cash + pos_value,
        n_positions=len(positions),
    )


def get_trade_history(client: ClobClient) -> pd.DataFrame:
    trades = client.get_trades(pm_types.TradeParams())
    if not trades:
        return pd.DataFrame()

    rows = []
    for t in trades:
        rows.append({
            "time": t.get("created_at", ""),
            "side": t.get("side", ""),
            "outcome": t.get("outcome", ""),
            "price": float(t.get("price", 0) or 0),
            "size": float(t.get("size", 0) or 0),
            "notional": float(t.get("price", 0) or 0) * float(t.get("size", 0) or 0),
            "status": t.get("status", ""),
            "market": t.get("market", "")[:20],
        })

    return pd.DataFrame(rows)
