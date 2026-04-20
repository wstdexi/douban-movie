from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_superuser: bool
    signature: str | None = None

    model_config = {"from_attributes": True}

