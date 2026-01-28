from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.models import Product , Category
from app.product.schemas import CategoryCreate


####################CATEGORY###################

async def create_category_in_db(session:AsyncSession,category:CategoryCreate):
    category = Category(name=category.name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

