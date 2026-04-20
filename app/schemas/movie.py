from pydantic import AliasChoices, BaseModel, Field, HttpUrl, model_validator
from app.schemas.common import PageParams


# 电影列表查询参数（分页 + 评分过滤）。
class MovieListQuery(PageParams):
    min_rating: float | None = Field(default=None, ge=0, le=10)
    max_rating: float | None = Field(default=None, ge=0, le=10)

    @model_validator(mode="after")
    def check_rating_range(self) -> "MovieListQuery":
        if self.min_rating is not None and self.max_rating is not None and self.min_rating > self.max_rating:
            raise ValueError("min_rating cannot exceed max_rating")
        return self

#。 基础的电影参数结构
class MovieBase(BaseModel):
    title: str
    rating: float
    comments_count: int = Field(validation_alias=AliasChoices("comments_count", "votes"))
    quote: str | None = None
    url: HttpUrl

#  电影更新所需的结构
class MovieUpdate(BaseModel):
    title: str | None = None
    rating: float | None = None
    comments_count: int | None = Field(
        default=None, validation_alias=AliasChoices("comments_count", "votes")
    )
    quote: str | None = None
    url: HttpUrl | None = None

#  输出电影结构
class OutMovie(BaseModel):
    id: int
    title: str
    rating: float
    comments_count: int
    quote: str | None = None
    url: HttpUrl

    model_config = {"from_attributes": True}