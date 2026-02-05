from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

import stripe

from app.cart.models import Cart, CartItem
from app.product.models import Product
from app.order.models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
)

# stripe.api_key = settings.STRIPE_SECRET_KEY


async def checkout_cart(
    db: AsyncSession,
    user_id: int,
    payment_method: PaymentMethod,
):
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
        payment_method=payment_method,
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

    client_secret = None

    # 6️⃣ Payment handling
    if payment_method == PaymentMethod.stripe:
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # cents
            currency="usd",
            metadata={"order_id": order.id},
        )
        order.stripe_payment_intent_id = intent.id
        client_secret = intent.client_secret

    elif payment_method == PaymentMethod.cod:
        # 🚚 Cash on Delivery → order is confirmed, NOT paid
        order.status = OrderStatus.confirmed

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method",
        )

    # 7️⃣ Clear cart
    await db.delete(cart)

    # 8️⃣ Commit everything
    await db.commit()
    await db.refresh(order)

    return order, client_secret
