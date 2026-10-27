"""In-memory Order REST API (assignment Question 2, Part A)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Order API", version="1.0.0")

_orders: dict[int, dict[str, Any]] = {}
_next_id = 1


class CreateOrderBody(BaseModel):
    item: str = Field(..., min_length=1)
    quantity: int


class OrderResponse(BaseModel):
    id: int
    item: str
    quantity: int
    status: str


def _allocate_id() -> int:
    global _next_id
    order_id = _next_id
    _next_id += 1
    return order_id


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(body: CreateOrderBody) -> OrderResponse:
    if body.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="quantity must be greater than 0",
        )
    order_id = _allocate_id()
    order = {
        "id": order_id,
        "item": body.item,
        "quantity": body.quantity,
        "status": "created",
    }
    _orders[order_id] = order
    return OrderResponse(**order)


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int) -> OrderResponse:
    if order_id < 1:
        raise HTTPException(status_code=400, detail="id must be a positive integer")
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"order {order_id} not found")
    return OrderResponse(**order)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders() -> list[OrderResponse]:
    return [OrderResponse(**o) for o in _orders.values()]
