from pydantic import AliasChoices, BaseModel, Field, HttpUrl

#
class MoviePageList(BaseModel):
    skip: int
    limit: int
    min_rating: float | None = None
    max_rating: float | None = None

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