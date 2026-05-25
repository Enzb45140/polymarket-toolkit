import json
import requests
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from py_clob_client.client import ClobClient
from src.client import GAMMA_BASE


@dataclass
class MarketInfo:
    condition_id: str
    question: str
    yes_token_id: str
    no_token_id: str
    active: bool
    end_date: Optional[str]
    gamma_volume: Optional[float] = None


def _iter_markets(client: ClobClient, max_pages: int = 4):
    cursor = None
    for _ in range(max_pages):
        params = {"next_cursor": cursor} if cursor else {}
        resp = client.get_markets(**params)
        data = resp if isinstance(resp, list) else resp.get("data", [])
        if not data:
            break
        yield from data
        cursor = resp.get("next_cursor") if isinstance(resp, dict) else None
        if not cursor:
            break


def _parse_token_ids(market: dict) -> tuple[str, str]:
    tokens = market.get("tokens", [])
    yes = next((t["token_id"] for t in tokens if t.get("outcome") == "Yes"), None)
    no = next((t["token_id"] for t in tokens if t.get("outcome") == "No"), None)
    return yes, no


def _rank_by_gamma_volume(condition_ids: list[str], chunk_size: int = 80) -> dict[str, float]:
    volumes = {}
    for i in range(0, len(condition_ids), chunk_size):
        chunk = condition_ids[i:i + chunk_size]
        params = {"condition_ids": ",".join(chunk), "_limit": chunk_size}
        try:
            r = requests.get(f"{GAMMA_BASE}/markets", params=params, timeout=20)
            r.raise_for_status()
            for m in r.json():
                cid = m.get("conditionId") or m.get("condition_id")
                vol = float(m.get("volume", 0) or 0)
                if cid:
                    volumes[cid] = vol
        except Exception:
            pass
    return volumes


def search_markets(
    keyword: str,
    client: Optional[ClobClient] = None,
    max_pages: int = 4,
    top_n: int = 20,
) -> pd.DataFrame:
    if client is None:
        from src.client import get_readonly_client
        client = get_readonly_client()

    pool = list(_iter_markets(client, max_pages=max_pages))
    kw = keyword.lower()
    hits = [m for m in pool if kw in json.dumps(m).lower()]

    condition_ids = [m.get("condition_id") for m in hits if m.get("condition_id")]
    volumes = _rank_by_gamma_volume(condition_ids)

    rows = []
    for m in hits:
        cid = m.get("condition_id", "")
        yes, no = _parse_token_ids(m)
        rows.append({
            "question": m.get("question") or m.get("title", ""),
            "condition_id": cid,
            "yes_token_id": yes,
            "no_token_id": no,
            "active": m.get("active", False),
            "end_date": m.get("end_date_iso"),
            "gamma_volume": volumes.get(cid, 0),
        })

    df = pd.DataFrame(rows).sort_values("gamma_volume", ascending=False).head(top_n)
    return df.reset_index(drop=True)


def get_market_by_slug(event_slug: str) -> list[MarketInfo]:
    r = requests.get(f"{GAMMA_BASE}/events/slug/{event_slug}", timeout=20)
    r.raise_for_status()
    event = r.json()
    markets = event.get("markets", [])

    result = []
    for m in markets:
        token_ids = m.get("clobTokenIds") or []
        if isinstance(token_ids, str):
            token_ids = json.loads(token_ids)
        if len(token_ids) < 2:
            continue
        result.append(MarketInfo(
            condition_id=m.get("id", ""),
            question=m.get("question", ""),
            yes_token_id=token_ids[0],
            no_token_id=token_ids[1],
            active=m.get("active", False),
            end_date=m.get("endDate"),
        ))
    return result
