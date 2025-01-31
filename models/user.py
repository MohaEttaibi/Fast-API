from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    # id: int | None = None
    id: Optional[int] = None
    email: str

class UserIn(User):
    password: str