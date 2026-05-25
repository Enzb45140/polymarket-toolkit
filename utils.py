import json
import re


def extract_event_slug(url_or_slug: str) -> str:
    match = re.search(r"/event/([^/?#]+)", url_or_slug)
    return match.group(1) if match else url_or_slug


def parse_token_ids(raw: str | list) -> list[str]:
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def format_usdc(value: float) -> str:
    return f"${value:,.2f}"


def mask_id(order_id: str, visible: int = 6) -> str:
    return order_id[:visible] + "*" * max(0, len(order_id) - visible)
