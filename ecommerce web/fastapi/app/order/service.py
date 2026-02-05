# app/order/services.py
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.cart.models import Cart, CartItem
from app.product.models import Product
from app.order.models import Order, OrderItem, OrderStatus


async def checkout_cart(
    db: AsyncSession,
    user_id: int,
) -> Order:
    # 1️⃣ Fetch cart with items & products
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

    total_amount = 0
    order_items: list[OrderItem] = []

    # 2️⃣ Validate stock & calculate totals
    for item in cart.items:
        product = item.product

        if item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.title}",
            )

        subtotal = product.price * item.quantity
        total_amount += subtotal

        order_items.append(
            OrderItem(
                product_id=product.id,
                product_title=product.title,
                price=product.price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )

    # 3️⃣ Create Order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.pending,
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
    await db.delete(cart)

    # 7️⃣ Commit everything
    await db.commit()
    await db.refresh(order)

    return order
