from decimal import Decimal

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

import stripe

from app.cart.models import Cart, CartItem
from app.order.models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
)
from app.core.config import settings


async def checkout_cart(
    db: AsyncSession,
    user_id: int,
    payment_method: PaymentMethod,
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

        price = Decimal(str(product.price))  # ✅ FIX
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

    # 3️⃣ Create order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.pending,
        payment_method=payment_method,
        payment_status="pending",
    )
    db.add(order)
    await db.flush()

    # 4️⃣ Attach items
    for item in order_items:
        item.order_id = order.id
        db.add(item)

    # 5️⃣ Reduce stock
    for item in cart.items:
        item.product.stock_quantity -= item.quantity

    client_secret = None

    # 6️⃣ Payment handling
    if payment_method == PaymentMethod.stripe:
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(
                status_code=500,
                detail="Stripe is not configured",
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY

        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency="usd",
            metadata={"order_id": str(order.id)},
        )

        order.stripe_payment_intent_id = intent.id
        client_secret = intent.client_secret

    elif payment_method == PaymentMethod.cod:
        order.status = OrderStatus.confirmed
        order.payment_status = "pending"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method",
        )

    # 7️⃣ Clear cart
    for item in cart.items:
        await db.delete(item)
    await db.delete(cart)

    # 8️⃣ Commit
    await db.commit()
    await db.refresh(order)

    return order, client_secret
