import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
GAMMA_BASE = "https://gamma-api.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"


def get_readonly_client() -> ClobClient:
    return ClobClient(HOST)


def get_authenticated_client() -> ClobClient:
    load_dotenv()
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
    signature_type = int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "0"))
    funder = os.getenv("POLYMARKET_FUNDER")

    if not private_key or not funder:
        raise EnvironmentError("POLYMARKET_PRIVATE_KEY and POLYMARKET_FUNDER must be set in .env")

    client = ClobClient(
        HOST,
        key=private_key,
        chain_id=CHAIN_ID,
        signature_type=signature_type,
        funder=funder,
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    return client
