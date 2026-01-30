# app/db/__init__.py
from app.db.config import engine
from app.db.base import Base
from app.product import models  # import all models so they register with Base

async def init_db():
    """
    Initialize the database and create all tables.
    Call this on FastAPI startup.
    """
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized and tables created.")
