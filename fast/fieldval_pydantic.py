from fastapi import FastAPI

from pydantic import BaseModel, field_validator


#TODO Request body + Validation
class User(BaseModel):
    name: str
    age: int
    email: str | None = None
    price: float | None = None

    @field_validator("age", mode="before") # by defualt mode is after
    @classmethod
    def age_must_be_positive(cls, v):
        if 0 < v < 40:
            return v
        else:
            raise ValueError("Age must be between 0 and 40")

    @field_validator("email")
    @classmethod
    def email_sep(cls, value):
        valid_domains = ["gmail.com", "yahoo.com", "hotmail.com"]
        given_domain = value.split("@")[-1]
        if given_domain not in valid_domains:
            raise ValueError("Email must be from a valid domain")
        return value

app = FastAPI()



#TODO Request body

@app.post("/users/")
async def read_item(instance: User):
    return instance


#TODO Request body + path parameters

@app.put("/users/{id}")
async def update_item(id: int, instance: User):
    return {"id": id, **instance.model_dump()}
