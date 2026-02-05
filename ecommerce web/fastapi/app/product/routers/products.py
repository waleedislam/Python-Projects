from fastapi import status
from typing import Annotated
from fastapi import APIRouter,Depends,UploadFile,File,Form
from app.db.session import SessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.schemas import ProductBase,PaginatedProductOut,ProductOut,ProductCreate,ProductUpdate
from app.user.models import User
from app.product.services import Create_product, get_product_by_slug_service, get_products_service

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def prod_create(
    title: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_ids: str | None = Form(None),  # ✅ FIX HERE
    image_url: UploadFile = File(None),
    session: AsyncSession = Depends(SessionDep),
):
    category_ids_list = (
        [int(x) for x in category_ids.split(",")]
        if category_ids else []
    )

    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_ids=category_ids_list
    )

    return await Create_product(session, data, image_url)

@router.get("/", response_model=PaginatedProductOut)
async def get_products(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
    session: AsyncSession = Depends(SessionDep),
):
    return await get_products_service(
        session,
        page,
        limit,
        search,
        category_id,
        min_price,
        max_price,
        sort,
    )

@router.get(
    "/slug/{slug}",
    response_model=ProductOut,
)
async def get_product_by_slug(
    slug: str,
    session: AsyncSession = Depends(SessionDep),
):
    return await get_product_by_slug_service(session, slug)