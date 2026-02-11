# app/order/routers.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionDep
from app.user.deps import get_current_user
from app.user.models import User

from app.order import service, schemas

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/checkout",
    response_model=schemas.CheckoutResponse,
)
async def checkout(
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    order = await service.checkout_cart(
        db=db,
        user_id=current_user.id,
    )

    return {
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
    }

# GET /api/orders/my-orders
@router.get("/my-orders", response_model=list[schemas.OrderResponse])
async def my_orders(
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user)
):
    return await service.get_user_orders(db, current_user.id)

# GET /api/orders/{order_id}
@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user)
):
    return await service.get_single_order(db, current_user.id, order_id)

# PUT /api/orders/{order_id}/cancel
@router.put("/{order_id}/cancel", response_model=schemas.CancelOrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user)
):
    order = await service.cancel_order(db, current_user.id, order_id)

    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.status
    }