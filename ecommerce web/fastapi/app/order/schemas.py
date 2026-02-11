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
    items: List[OrderItemOut]

    model_config = {
        "from_attributes": True
    }


class CheckoutResponse(BaseModel):
    order_id: int
    status: OrderStatus
    total_amount: Decimal

class OrderResponse(OrderOut):
    pass


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]


class CancelOrderResponse(BaseModel):
    message: str
    order_id: int
    status: str
