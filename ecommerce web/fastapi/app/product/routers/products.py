from fastapi import status
from typing import Annotated
from fastapi import APIRouter,Depends,UploadFile,File,Form
from app.db import session
from app.product.schemas import ProductBase,PaginatedProductOut,ProductOut,ProductCreate,ProductUpdate
from app.db.config import SessionDep
from app.user.models import User
from app.product.services import Create_product

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def prod_create(
    title: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_ids: list[int] = Form(None),
    image_url: UploadFile = File(None), # This captures the actual file
):
    # Reconstruct the Pydantic model from form data
    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_ids=category_ids
    )
    
    return await Create_product(session, data, image_url)