from fastapi import FastAPI

from app.product.routers.category import router as category_router
from app.user.routers import router as user_router

app = FastAPI()

# -------------------------
# Product Categories Routes
# -------------------------
app.include_router(
    category_router,
    prefix="/api/products-category",
    tags=["Product Categories"]
)

# -------------------------
# User / Auth Routes
# -------------------------
app.include_router(
    user_router,
    prefix="/api/users",
    tags=["Users"]
)
