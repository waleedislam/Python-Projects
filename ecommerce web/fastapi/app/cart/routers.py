from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionDep
from app.user.deps import get_current_user
from app.user.models import User
from app.cart import schemas, services

router = APIRouter()

## ADD ITEM TO CART
@router.post(
    "/items",
    response_model=schemas.CartOut,   # ✅ FIXED
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    data: schemas.CartItemCreate,
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    await services.add_item_to_cart(
        db=db,
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity,
    )

    return await services.get_cart(db, current_user.id)


## GET CART
@router.get(
    "",
    response_model=schemas.CartOut,   # ✅ FIXED
)
async def get_my_cart(
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    return await services.get_cart(db, current_user.id)


## UPDATE CART ITEM QUANTITY
@router.put(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_cart_item(
    item_id: int,
    data: schemas.CartItemUpdate,
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    await services.update_cart_item_quantity(
        db=db,
        user_id=current_user.id,
        item_id=item_id,
        quantity=data.quantity,
    )


## REMOVE CART ITEM
@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_item_from_cart(
    item_id: int,
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    await services.remove_cart_item(
        db=db,
        user_id=current_user.id,
        item_id=item_id,
    )


## CLEAR CART
@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_my_cart(
    db: AsyncSession = Depends(SessionDep),
    current_user: User = Depends(get_current_user),
):
    await services.clear_cart(db, current_user.id)
