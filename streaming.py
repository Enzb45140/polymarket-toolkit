import asyncio
import json
import logging
from collections import defaultdict
from typing import Callable, Optional
import websockets

WSS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
logger = logging.getLogger(__name__)


class LocalOrderbook:
    def __init__(self):
        self.bids: dict[float, float] = {}
        self.asks: dict[float, float] = {}
        self.last_trade_price: Optional[float] = None

    def apply_snapshot(self, bids: list, asks: list):
        self.bids = {float(b["price"]): float(b["size"]) for b in bids}
        self.asks = {float(a["price"]): float(a["size"]) for a in asks}

    def apply_delta(self, changes: list):
        for change in changes:
            price = float(change["price"])
            size = float(change["size"])
            side = change.get("side", "").lower()
            book = self.bids if side == "buy" else self.asks
            if size == 0:
                book.pop(price, None)
            else:
                book[price] = size

    @property
    def best_bid(self) -> Optional[float]:
        return max(self.bids) if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        return min(self.asks) if self.asks else None

    @property
    def mid(self) -> Optional[float]:
        if self.best_bid and self.best_ask:
            return (self.best_bid + self.best_ask) / 2
        return None

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None


async def stream_market(
    asset_ids: list[str],
    on_update: Callable[[str, LocalOrderbook], None],
    duration_seconds: int = 60,
    ping_interval: int = 5,
):
    books: dict[str, LocalOrderbook] = defaultdict(LocalOrderbook)

    async with websockets.connect(WSS_URL, ping_interval=None) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": asset_ids,
            "custom_feature_enabled": True,
        }))

        async def heartbeat():
            while True:
                await asyncio.sleep(ping_interval)
                await ws.send("PING")

        hb = asyncio.create_task(heartbeat())

        try:
            async with asyncio.timeout(duration_seconds):
                while True:
                    raw = await ws.recv()
                    if raw == "PONG":
                        continue

                    payload = json.loads(raw)
                    events = payload if isinstance(payload, list) else [payload]

                    for msg in events:
                        event_type = msg.get("event_type") or msg.get("type")
                        asset_id = msg.get("asset_id", "")
                        book = books[asset_id]

                        if event_type == "book":
                            book.apply_snapshot(msg.get("bids", []), msg.get("asks", []))
                        elif event_type == "price_change":
                            book.apply_delta(msg.get("changes", []))
                        elif event_type == "last_trade_price":
                            book.last_trade_price = float(msg.get("price", 0))

                        on_update(asset_id, book)

        except TimeoutError:
            logger.info("Stream ended after %ds", duration_seconds)
        finally:
            hb.cancel()


def run_stream(asset_ids: list[str], on_update: Callable, duration_seconds: int = 60):
    asyncio.run(stream_market(asset_ids, on_update, duration_seconds))
