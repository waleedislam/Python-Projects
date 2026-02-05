# app/order/schemas.py

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from app.order.models import OrderStatus, PaymentMethod, PaymentMethod


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

class CheckoutRequest(BaseModel):
    payment_method: PaymentMethod


class CheckoutResponse(BaseModel):
    order_id: int
    status: OrderStatus
    total_amount: float
    client_secret: Optional[str] = None    