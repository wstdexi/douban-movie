from pydantic import AliasChoices, BaseModel, Field, HttpUrl


class MovieBase(BaseModel):
    title: str
    rating: float
    comments_count: int = Field(validation_alias=AliasChoices("comments_count", "votes"))
    quote: str | None = None
    url: HttpUrl


class MovieUpdate(BaseModel):
    title: str | None = None
    rating: float | None = None
    comments_count: int | None = Field(
        default=None, validation_alias=AliasChoices("comments_count", "votes")
    )
    quote: str | None = None
    url: HttpUrl | None = None


class OutMovie(BaseModel):
    id: int
    title: str
    rating: float
    comments_count: int
    quote: str | None = None
    url: HttpUrl

    model_config = {"from_attributes": True}