from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.product.schemas import ProductOut


#### Add to cart ####
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


#### Update cart item quantity ####
class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


#### Cart item response ####
class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    subtotal: float

    # ✅ THIS IS THE CRITICAL FIX
    model_config = ConfigDict(from_attributes=True)

#### FULL CART RESPONSE (🔥 THIS WAS MISSING 🔥)
class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total_price: float

    model_config = {
        "from_attributes": True
    }