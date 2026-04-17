from fastapi import FastAPI

from app.controllers import movie_controller

app = FastAPI(title="Douban Movies API", version="1.0.0")
app.include_router(movie_controller.router)

# Keep these aliases for gRPC service reuse and scripts.
list_movies = movie_controller.list_movies
get_movie = movie_controller.get_movie
create_movie_api = movie_controller.create_movie_api
update_movie_api = movie_controller.update_movie_api
delete_movie_api = movie_controller.delete_movie_api
clear_movies_api = movie_controller.clear_movies_api
export_movies_csv = movie_controller.export_movies_csv


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)