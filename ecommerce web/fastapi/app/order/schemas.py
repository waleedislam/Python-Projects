# app/order/schemas.py

from pydantic import BaseModel
from typing import List
from decimal import Decimal
from app.order.models import OrderStatus


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_title: str
    price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {
        "from_attributes": True
    }


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: Decimal
    stripe_payment_intent_id: str | None
    items: List[OrderItemOut]

    model_config = {
        "from_attributes": True
    }
