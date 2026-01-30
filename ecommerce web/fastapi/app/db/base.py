# app/db/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

# Base class for all models
class Base(AsyncAttrs, DeclarativeBase):
    pass
