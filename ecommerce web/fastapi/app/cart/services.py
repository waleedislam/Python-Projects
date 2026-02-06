from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.cart.models import Cart, CartItem
from app.product.models import Product


# -------------------------
# Cart helpers
# -------------------------

async def get_or_create_cart(
    db: AsyncSession,
    user_id: int,
) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items))
    )
    cart = result.scalars().first()

    if cart:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart


# -------------------------
# Add item to cart
# -------------------------

async def add_item_to_cart(
    db: AsyncSession,
    user_id: int,
    product_id: int,
    quantity: int,
) -> CartItem:
    # 1️⃣ Get or create cart
    cart = await get_or_create_cart(db, user_id)

    # 2️⃣ Get product
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # 3️⃣ Check existing cart item
    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    )
    cart_item = result.scalar_one_or_none()

    # 4️⃣ Update or create
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)

    await db.commit()

    # 🔥 CRITICAL FIX: reload with product relationship
    result = await db.execute(
        select(CartItem)
        .where(CartItem.id == cart_item.id)
        .options(selectinload(CartItem.product))
    )
    cart_item = result.scalar_one()

    return cart_item


# -------------------------
# Get cart
# -------------------------

async def get_cart(
    db: AsyncSession,
    user_id: int,
) -> dict:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product)
        )
    )
    cart = result.scalars().first()

    if not cart:
        return {
            "id": None,
            "items": [],
            "total_price": 0,
        }

    items = []
    total_price = 0

    for item in cart.items:
        subtotal = item.product.price * item.quantity
        total_price += subtotal

        items.append({
            "id": item.id,
            "product": item.product,
            "quantity": item.quantity,
            "subtotal": subtotal,
        })

    return {
        "id": cart.id,
        "items": items,
        "total_price": total_price,
    }


# -------------------------
# Update quantity
# -------------------------

async def update_cart_item_quantity(
    db: AsyncSession,
    user_id: int,
    item_id: int,
    quantity: int,
):
    result = await db.execute(
        select(CartItem)
        .join(Cart)
        .where(
            CartItem.id == item_id,
            Cart.user_id == user_id,
        )
        .options(selectinload(CartItem.product))
    )
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero",
        )

    if quantity > cart_item.product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock",
        )

    cart_item.quantity = quantity
    await db.commit()


# -------------------------
# Remove item
# -------------------------

async def remove_cart_item(
    db: AsyncSession,
    user_id: int,
    item_id: int,
):
    result = await db.execute(
        select(CartItem)
        .join(Cart)
        .where(
            CartItem.id == item_id,
            Cart.user_id == user_id,
        )
    )
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    await db.delete(cart_item)
    await db.commit()


# -------------------------
# Clear cart
# -------------------------

async def clear_cart(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = result.scalars().first()

    if cart:
        await db.delete(cart)
        await db.commit()

#stock