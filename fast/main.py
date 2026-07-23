import asyncio

from fastapi import FastAPI

app = FastAPI()

# TODO routing

@app.get("/")
def read_root():
    return {"Hello": "World"}




# TODO path parameters

# @app.get("/items/{item_id}")
# async def read_item(item_id):  # accept any type
#     return {"item_id": item_id}

@app.get("/items/{item_id}")
async def read_item(item_id: int): # accept only int type
    return {"item_id": item_id}



# TODO query parameters

@app.get('/items')
def read_item(name: str, age: int):
    return {"name": name, "age": age}

# @app.get('/items')
# async def read_item(name: str, age: int):
#     await asyncio.sleep(1)  # simulate a delay
#     return {"name": name, "age": age}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 1, limit: int = 1):
    return fake_items_db[skip : skip + limit]


# TODO optional query parameters

@app.get("/items-optional/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}