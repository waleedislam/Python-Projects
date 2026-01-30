from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.product.models import Category
from app.product.schemas import CategoryCreate
from app.product.schemas import ProductBase,PaginatedProductOut,ProductOut,ProductCreate,ProductUpdate

async def create_category_in_db(
    session: AsyncSession,
    category_in: CategoryCreate
):
    # Check if category already exists
    result = await session.execute(
        select(Category).where(Category.name == category_in.name)
    )
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

    category = Category(name=category_in.name)
    session.add(category)

    try:
        await session.commit()
        await session.refresh(category)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create category"
        )

    return category

async def get_all_categories(session:AsyncSession):
    stmt = select(Category)
    result = await session.execute(stmt)
    return result.scalars().all()

async def delete_category(session:AsyncSession,category_id:int):
    category = await session.get(Category,category_id)
    if not category:
        return False
    else:
        await session.delete(category)
        await session.commit()
        return True
    
    ################Product APIs ###################

async def Create_product(session:AsyncSession,data:ProductCreate,image_url:UploadFile | None=None):
    if data.stock_quantity<0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Stock Quantity can't be negative")
    categories=[]
    if data.category_ids:
        category_stmt = select(Category).where(Category.id.in_(data.category_ids)) 
        category_result =await session.execute(category_stmt)
        categories = category_result.scalars().all()

    product_dict = data.model_dump(exclude={"category_ids"})
