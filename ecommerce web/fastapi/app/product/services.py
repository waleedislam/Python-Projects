from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.product.models import Category, Product
from app.product.schemas import CategoryCreate
from app.product.schemas import ProductBase,PaginatedProductOut,ProductOut,ProductCreate,ProductUpdate
from app.product.utils import generate_slug, save_upload_file

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
    
    image_path = await save_upload_file(image_url,"images")

    categories=[]
    if data.category_ids:
        category_stmt = select(Category).where(Category.id.in_(data.category_ids)) 
        category_result =await session.execute(category_stmt)
        categories = category_result.scalars().all()

    product_dict = data.model_dump(exclude={"category_ids"})
    if not product_dict.get("slug"):
       product_dict["slug"]=generate_slug(product_dict.get("title")) 

    new_product = Product(**product_dict,image_url=image_path,categories=categories)
    session.add(new_product)   
    await session.commit()
    await session.refresh(new_product)
    return new_product


async def get_products_service(
    session: AsyncSession,
    page: int,
    limit: int,
    search: str | None,
    category_id: int | None,
    min_price: float | None,
    max_price: float | None,
    sort: str | None,
):
    stmt = select(Product).options(
        selectinload(Product.categories)
    )

    # SEARCH
    if search:
        stmt = stmt.where(Product.title.ilike(f"%{search}%"))

    # CATEGORY FILTER
    if category_id:
        stmt = stmt.join(Product.categories).where(
            Category.id == category_id
        )

    # PRICE FILTER
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # SORTING
    if sort == "price_asc":
        stmt = stmt.order_by(Product.price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Product.price.desc())
    else:
        stmt = stmt.order_by(Product.id.desc())

    # TOTAL COUNT
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(total_stmt)
    total = total_result.scalar()

    # PAGINATION
    stmt = stmt.offset((page - 1) * limit).limit(limit)

    result = await session.execute(stmt)
    products = result.scalars().unique().all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": products,
    }


async def get_product_by_slug_service(
    session: AsyncSession,
    slug: str,
):
    stmt = (
        select(Product)
        .where(Product.slug == slug)
        .options(
            selectinload(Product.categories)
        )
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product
