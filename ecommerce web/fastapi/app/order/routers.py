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
    response_model=schemas.OrderOut,
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    order = await service.checkout_cart(
        db=db,
        user_id=current_user.id,
    )
    return order
