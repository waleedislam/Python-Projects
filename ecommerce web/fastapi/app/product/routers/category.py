from fastapi import APIRouter , Depends , HTTPException , status
from app.db.config import SessionDep
from app.product.schemas import CategoryCreate,CategoryOut
from app.product.services import create_category_in_db
from app.user.deps import admin_only
from app.product.services import get_all_categories,delete_category

router = APIRouter()


@router.post('/' , response_model=CategoryOut)
async def category_create(session:SessionDep,category:CategoryCreate):
    return await create_category_in_db(session,category)

@router.get("/get-all-categories",response_model=list[CategoryOut])
async def list_categories(session:SessionDep):
    return await get_all_categories(session)

@router.delete("/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(session:SessionDep,category_id:int):
    success = await delete_category(session,category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category Not Found")
        
