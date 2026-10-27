"""Send 8 GET requests through Kong to demonstrate 5 req/min rate limiting."""

from __future__ import annotations

import json
import sys

import httpx

KONG_ORDERS_URL = "http://127.0.0.1:8000/api/orders"


def main() -> None:
    print(f"Target: {KONG_ORDERS_URL}\n")
    with httpx.Client(timeout=10.0) as client:
        for i in range(1, 9):
            response = client.get(KONG_ORDERS_URL)
            limit = response.headers.get("x-ratelimit-limit-minute", "-")
            remaining = response.headers.get("x-ratelimit-remaining-minute", "-")
            print(
                f"Request {i}: HTTP {response.status_code} "
                f"(limit={limit}, remaining={remaining})"
            )
            if response.status_code == 429:
                try:
                    print("  body:", json.dumps(response.json()))
                except json.JSONDecodeError:
                    print("  body:", response.text[:200])
    print("\nExpect HTTP 200 for the first 5 requests and HTTP 429 afterward.")


if __name__ == "__main__":
    try:
        main()
    except httpx.ConnectError as exc:
        print("Could not connect to Kong. Start the API and Kong first.", file=sys.stderr)
        raise SystemExit(1) from exc
