from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class ProductBase(BaseModel):
    title:str
    description:str | None = None
    price:float=Field(ge=0)
    stock_quantity:int =Field(ge=0)

class ProductCreate(ProductBase):
    category_ids:list[int] | None=None

class ProductOut(ProductBase):
    id:int
    title:str
    description:str
    slug:str
    price:float
    categories:list[CategoryOut]=[]
    image_url:str | None=None
    model_config={
        "from_attributes":True
    }

class PaginatedProductOut(BaseModel):
    total:int
    page:int
    limit:int
    items:list[ProductOut]

class ProductUpdate(BaseModel):
    title:str
    description:str
    price:float
    image_url:str | None=None
    category_ids:list[int] | None=None
    stock_quantity:int |None=None
    model_config={
        "from_attributes":True
    }     