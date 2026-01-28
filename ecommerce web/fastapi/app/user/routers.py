from sqlalchemy import select
from app.core.security import create_access_token, hash_password, verify_password
from app.db.config import SessionDep
from app.user.deps import get_current_user
from app.user.models import User
from app.user.schemas import UserLogin, UserOut, UserSignup
from fastapi import APIRouter, Depends, HTTPException

router=APIRouter()


@router.post("/signup", response_model=UserOut)
async def signup(user_data: UserSignup, session: SessionDep):
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/login")
async def login(user_data: UserLogin, session: SessionDep):
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
