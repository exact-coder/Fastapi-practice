from pydantic import BaseModel, Field

class UserCreateModel(BaseModel):
    username: str =Field(min_length=4,max_length=30)
    email: str = Field(max_length=50)
    password: str = Field(min_length=5)