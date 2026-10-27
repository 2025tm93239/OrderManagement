"""
MCP server exposing the order_api tool (assignment Question 2, Part B).

Calls the Order API through Kong at ORDER_API_BASE_URL (default http://127.0.0.1:8000/api/orders).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

SCHEMA_PATH = Path(__file__).with_name("order_tool_schema.json")
DEFAULT_BASE = "http://127.0.0.1:8000/api/orders"
BASE_URL = os.environ.get("ORDER_API_BASE_URL", DEFAULT_BASE).rstrip("/")

mcp = FastMCP("order-mcp-server")


class OrderToolInput(BaseModel):
    action: str = Field(..., pattern="^(create_order|get_order|list_orders)$")
    item: str | None = None
    quantity: int | None = None
    id: int | None = Field(None, alias="id")

    model_config = {"populate_by_name": True}

    @field_validator("action")
    @classmethod
    def normalize_action(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def check_action_fields(self) -> OrderToolInput:
        if self.action == "create_order":
            if not self.item or not self.item.strip():
                raise ValueError("item is required for create_order")
            if self.quantity is None:
                raise ValueError("quantity is required for create_order")
            if self.quantity <= 0:
                raise ValueError("quantity must be greater than 0")
        elif self.action == "get_order":
            if self.id is None:
                raise ValueError("id is required for get_order")
            if self.id < 1:
                raise ValueError("id must be a positive integer")
        return self


def _load_tool_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _call_api(payload: OrderToolInput) -> dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        if payload.action == "create_order":
            response = client.post(
                BASE_URL,
                json={"item": payload.item, "quantity": payload.quantity},
            )
        elif payload.action == "get_order":
            response = client.get(f"{BASE_URL}/{payload.id}")
        else:
            response = client.get(BASE_URL)

    try:
        body: Any = response.json()
    except json.JSONDecodeError:
        body = {"raw": response.text}

    return {
        "status_code": response.status_code,
        "body": body,
    }


@mcp.tool(name="order_api", description=_load_tool_schema()["description"])
def order_api(
    action: str,
    item: str | None = None,
    quantity: int | None = None,
    id: int | None = None,
) -> str:
    """Unified Order API tool: create_order, get_order, or list_orders."""
    try:
        payload = OrderToolInput(
            action=action,
            item=item,
            quantity=quantity,
            id=id,
        )
    except ValidationError as exc:
        return json.dumps(
            {"error": "invalid_input", "details": json.loads(exc.json())},
            indent=2,
        )

    result = _call_api(payload)
    return json.dumps(result, indent=2)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
