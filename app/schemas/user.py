from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    hashed_password: str
    is_superuser: bool = False
    signature: str | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    is_superuser: bool | None = None
    signature: str | None = None
