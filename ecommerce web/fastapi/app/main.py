from fastapi import FastAPI
from app.db import init_db
from app.product.routers.category import router as category_router
from app.user.routers import router as user_router
from app.product.routers.products import router as prod_router
from app.cart.routers import router as cart_router
from app.order.routers import router as order_router

app = FastAPI()

# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
async def on_startup():
    await init_db()  # This will create tables

# -------------------------
# Routes
# -------------------------
app.include_router(
    category_router,
    prefix="/api/products-category",
    tags=["Product Categories"]
)

app.include_router(
    prod_router,
    prefix="/api/products",
    tags=["Products"]
)

app.include_router(
    user_router,
    prefix="/api/users",
    tags=["Users"]
)

app.include_router(
    cart_router,
    prefix="/api/cart",
    tags=["Cart"]
)

app.include_router(
    order_router,
    prefix="/api/orders",
    tags=["Orders"],
)
