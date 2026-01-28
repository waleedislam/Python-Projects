from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    first_name:str
    last_name:str
    phone:str
    email:EmailStr
    password:str
    role:str = "user"


class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserOut(BaseModel):
    id:int
    first_name:str
    last_name:str
    phone:str
    email:EmailStr
    role:str

    class Config:
        form_attributes=True
     