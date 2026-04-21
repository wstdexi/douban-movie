from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class CredentialsSchema(BaseModel):
    username: str = Field(title="Username",description="用户名")
    password: str = Field(description="密码")

    class Config:
        populate_by_name=True


class RegisterSchema(BaseModel):
    username: str = Field(min_length=1, max_length=100, description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(min_length=6, description="密码")
    signature: str | None = Field(default=None, max_length=100, description="个性签名")


class JWTOut(BaseModel):
    access_token: Annotated[str | None, Field(alias="token",description="请求token")] = None
    refresh_token: Annotated[str | None, Field(alias="refreshToken",description="刷新token")] = None

    class Config:
        populate_by_name = True

class JWTPayload(BaseModel):
    data: dict
    iat: datetime
    exp: datetime

    class Config:
        populate_by_name = True


__all__ = ["CredentialsSchema", "RegisterSchema", "JWTOut", "JWTPayload"]
