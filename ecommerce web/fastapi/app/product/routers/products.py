from typing import Annotated
from fastapi import APIRouter,Depends,UploadFile,File,Form
from app.product.schemas import ProductBase,PaginatedProductOut,ProductOut,ProductCreate,ProductUpdate
from app.db.config import SessionDep
from app.user.models import User
from app.product.services import Create_product

router = APIRouter()

@router.post("",response_model=ProductOut)
async def prod_create(
        session:SessionDep,
            title:str =Form(...),
            description:str =Form(...),
            price:float =Form(...),
            image_url:str =Form(...),
            category_ids:Annotated[list[int],Form()]=[],
            stock_quantity:int  =Form(...),
        ):
    data=ProductCreate(
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_ids=category_ids
    )
    return await Create_product(session,data,image_url)