from fastapi import FastAPI

from app.api.v1.route import movie_route

# 创建fastapi架构
app = FastAPI(title="豆瓣电影 API", version="1.0.0")

# 添加电影相关路由
app.include_router(movie_route.router)

# 保留这些别名，供 gRPC 服务和脚本复用。
list_movies = movie_route.list_movies
get_movie = movie_route.get_movie
create_movie_api = movie_route.create_movie_api
update_movie_api = movie_route.update_movie_api
delete_movie_api = movie_route.delete_movie_api
clear_movies_api = movie_route.clear_movies_api
export_movies_csv = movie_route.export_movies_csv


if __name__ == "__main__":
    import uvicorn
    print("http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)