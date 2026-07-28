from typing import Annotated, Any
from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []




# TODO status_code
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}


# TODO response_model
@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any: #return type of Any is used to avoid type checking errors but it optionally can be used to specify the return type of the function
    return item


@app.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]


# TODO: dependency used for sharing logic or avoiding redundancy
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

avoid_lil_bitredundency = Annotated[dict, Depends(common_parameters)]

@app.get("/items/")
async def read_items(commons: avoid_lil_bitredundency):
    return commons


@app.get("/users/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons



