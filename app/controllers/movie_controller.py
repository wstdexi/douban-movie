# 电影参数校验控制器：负责路由层输入参数校验与规范化。

from app.schemas.movie import MovieBase, MovieListQuery, MovieUpdate


class MovieRequestController:
    # 校验分页查询参数。
    def validate_list_query(self, query: MovieListQuery) -> None:
        if query.limit > 100:
            raise ValueError("limit cannot exceed 100")

    # 校验并规范化新增数据。
    def normalize_create_payload(self, movie_in: MovieBase) -> dict:
        movie_data = movie_in.model_dump()
        movie_data["url"] = str(movie_data["url"])
        return movie_data

    # 校验并规范化更新数据。
    def normalize_update_payload(self, movie_in: MovieUpdate) -> dict:
        update_data = movie_in.model_dump(exclude_unset=True)
        if "url" in update_data and update_data["url"] is not None:
            update_data["url"] = str(update_data["url"])
        return update_data


movie_request_controller = MovieRequestController()

