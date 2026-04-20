from pydantic import BaseModel, Field


# 通用分页参数结构（可被所有列表接口复用）。
class PageParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=10000)

