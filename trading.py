import logging
from typing import Optional
from py_clob_client.client import ClobClient
import py_clob_client.clob_types as pm_types
from py_clob_client.order_builder.constants import BUY, SELL

logger = logging.getLogger(__name__)


def place_limit_order(
    client: ClobClient,
    token_id: str,
    price: float,
    size: float,
    side: str,
) -> Optional[str]:
    assert side in ("BUY", "SELL"), "side must be 'BUY' or 'SELL'"
    assert 0 < price < 1, "price must be between 0 and 1"
    assert size > 0, "size must be positive"

    order_args = pm_types.OrderArgs(
        token_id=token_id,
        price=price,
        size=size,
        side=BUY if side == "BUY" else SELL,
    )
    signed = client.create_order(order_args)
    resp = client.post_order(signed, pm_types.OrderType.GTC)

    order_id = resp.get("orderID") if isinstance(resp, dict) else getattr(resp, "orderID", None)
    if order_id:
        logger.info("Order placed: %s %s @ %.4f x %.2f", side, token_id[:12], price, size)
    return order_id


def place_market_order(
    client: ClobClient,
    token_id: str,
    usdc_amount: float,
    side: str,
) -> Optional[str]:
    assert side in ("BUY", "SELL")
    assert usdc_amount > 0

    order_args = pm_types.MarketOrderArgs(
        token_id=token_id,
        amount=usdc_amount,
        side=BUY if side == "BUY" else SELL,
    )
    signed = client.create_market_order(order_args)
    resp = client.post_order(signed, pm_types.OrderType.FOK)

    order_id = resp.get("orderID") if isinstance(resp, dict) else getattr(resp, "orderID", None)
    return order_id


def cancel_order(client: ClobClient, order_id: str) -> bool:
    try:
        client.cancel(order_id)
        logger.info("Cancelled order %s", order_id[:10])
        return True
    except Exception as e:
        logger.error("Cancel failed: %s", e)
        return False


def cancel_all(client: ClobClient) -> bool:
    try:
        client.cancel_all()
        logger.info("All orders cancelled")
        return True
    except Exception as e:
        logger.error("Cancel all failed: %s", e)
        return False


def get_open_orders(client: ClobClient) -> list[dict]:
    orders = client.get_orders(pm_types.OpenOrderParams())
    return sorted(orders, key=lambda x: x.get("created_at", 0), reverse=True)
