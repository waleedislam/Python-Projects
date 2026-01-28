from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer,Boolean
from app.db.base import Base

class User(Base):
    __tablename__="users"

    id:Mapped[int] = mapped_column(primary_key=True)
    first_name:Mapped[str]=mapped_column(String(50))
    last_name:Mapped[str]=mapped_column(String(50))
    phone:Mapped[str]=mapped_column(String(20))
    email:Mapped[str]=mapped_column(String(255))
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[str]=mapped_column(String(20),default="user")
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
