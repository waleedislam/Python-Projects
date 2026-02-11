from decimal import Decimal

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.cart.models import Cart, CartItem
from app.order.models import (
    Order,
    OrderItem,
    OrderStatus,
)


async def checkout_cart(
    db: AsyncSession,
    user_id: int,
):
    # 1️⃣ Load cart
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product)
        )
    )
    cart = result.scalars().first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    total_amount = Decimal("0.00")
    order_items: list[OrderItem] = []

    # 2️⃣ Validate stock & calculate totals
    for item in cart.items:
        product = item.product

        if item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.title}",
            )

        price = Decimal(str(product.price))
        quantity = Decimal(item.quantity)

        subtotal = price * quantity
        total_amount += subtotal

        order_items.append(
            OrderItem(
                product_id=product.id,
                product_title=product.title,
                price=price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )

    # 3️⃣ Create order (COD only)
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.pending,  # COD orders are confirmed
    )

    db.add(order)
    await db.flush()  # get order.id

    # 4️⃣ Attach order items
    for item in order_items:
        item.order_id = order.id
        db.add(item)

    # 5️⃣ Reduce stock
    for item in cart.items:
        item.product.stock_quantity -= item.quantity

    # 6️⃣ Clear cart
    for item in cart.items:
        await db.delete(item)
    await db.delete(cart)

    # 7️⃣ Commit
    await db.commit()
    await db.refresh(order)

    return order

# 1️⃣ Get My Orders
async def get_user_orders(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

# 2️⃣ Get Single Order
async def get_single_order(db: AsyncSession, user_id: int, order_id: int):
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order

# 3️⃣ Cancel Order
async def cancel_order(db: AsyncSession, user_id: int, order_id: int):
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status not in ["pending", "accepted"]:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled at this stage"
        )

    order.status = "cancelled"
    await db.commit()
    await db.refresh(order)

    return order