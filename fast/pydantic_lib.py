from fastapi import FastAPI

from pydantic import AnyUrl, BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Annotated


#TODO Request body + Validation
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float # required field
    tax: float | None = None # option field


#Todo Request body + Advance validation
# class Item(BaseModel):
#     name: Annotated[str, Field(max_length=30, title="Name of the item", description="Name must be less than 30 characters")]
#     email: EmailStr
#     link_url: AnyUrl
#     price: float = Field(gt=0, strict=True)
#     age: int = Field(gt=0, lt=70, title="Age", description="Age must be between 0 and 70")
#     tax: float | None = None
#     category: Annotated[Optional[List[str]], Field(default=None, max_length=100)]
#     dic_desc: Dict[str, str]
    

app = FastAPI()



#TODO Request body

@app.post("/items/")
async def read_item(item: Item):
    return item

@app.post("/items/tax")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

#TODO Request body + path parameters

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}

#TODO Request body + path + query parameters
@app.put("/items/{item_id}/query")
async def update_item_with_query(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result