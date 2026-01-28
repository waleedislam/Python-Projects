from fastapi import APIRouter , Depends , HTTPException , status
from app.db.config import SessionDep
from app.product.schemas import CategoryCreate,CategoryOut
from app.product.services import create_category_in_db

router = APIRouter()


@router.post('/' , response_model=CategoryOut)
async def category_create(session:SessionDep,category:CategoryCreate):
    return await create_category_in_db(session,category)