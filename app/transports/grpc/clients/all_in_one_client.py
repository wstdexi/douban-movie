import argparse
import os

import grpc

from app.transports.grpc.clients.movie_client import MovieClient


# 命令行一体化客户端：用于演示和调用电影gRPC接口。
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="All-in-one gRPC movie client")
    parser.add_argument(
        "--target",
        default=os.getenv("GRPC_TARGET", "127.0.0.1:50051"),
        help="gRPC server target, e.g. grpc-server:50051",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run end-to-end CRUD demo")

    list_parser = subparsers.add_parser("list", help="List movies")
    list_parser.add_argument("--skip", type=int, default=0)
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.add_argument("--min-rating", type=float, default=None)
    list_parser.add_argument("--max-rating", type=float, default=None)

    get_parser = subparsers.add_parser("get", help="Get one movie by id")
    get_parser.add_argument("movie_id", type=int)

    create_parser = subparsers.add_parser("create", help="Create one movie")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--rating", type=float, required=True)
    create_parser.add_argument("--comments-count", type=int, required=True)
    create_parser.add_argument("--quote", required=True)
    create_parser.add_argument("--url", required=True)

    update_parser = subparsers.add_parser("update", help="Update one movie")
    update_parser.add_argument("movie_id", type=int)
    update_parser.add_argument("--title", default=None)
    update_parser.add_argument("--rating", type=float, default=None)
    update_parser.add_argument("--comments-count", type=int, default=None)
    update_parser.add_argument("--quote", default=None)
    update_parser.add_argument("--url", default=None)

    delete_parser = subparsers.add_parser("delete", help="Delete one movie by id")
    delete_parser.add_argument("movie_id", type=int)
    subparsers.add_parser("clear", help="Clear all movies")
    return parser


def print_movie(movie) -> None:
    print(
        f"[{movie.id}] {movie.title} | rating={movie.rating} | "
        f"comments={movie.comments_count} | quote={movie.quote} | url={movie.url}"
    )


def run_demo(client: MovieClient) -> None:
    movies = client.list_movies(skip=0, limit=5)
    print(f"列表查询返回 {len(movies)} 条:")
    for movie in movies:
        print_movie(movie)

    created = client.create_movie(
        title="grpc-temp-movie",
        rating=8.8,
        comments_count=123,
        quote="temporary test movie",
        url="https://example.com/grpc-temp-movie",
    )
    print("添加成功:")
    print_movie(created)
    print("查找成功:")
    print_movie(client.get_movie(created.id))
    print("更新成功:")
    print_movie(client.update_movie(created.id, quote="updated by grpc client", comments_count=456))
    print(f"删除成功: {client.delete_movie(created.id).message}")

    try:
        client.get_movie(created.id)
        print("异常: 删除后仍可查询到该电影")
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.NOT_FOUND:
            print("验证成功: 删除后查询不到，数据已恢复到无该记录状态")
        else:
            raise


def main() -> None:
    args = build_parser().parse_args()
    client = MovieClient(target=args.target)
    try:
        if args.command == "demo":
            run_demo(client)
        elif args.command == "list":
            movies = client.list_movies(
                skip=args.skip,
                limit=args.limit,
                min_rating=args.min_rating,
                max_rating=args.max_rating,
            )
            print(f"共返回 {len(movies)} 条")
            for movie in movies:
                print_movie(movie)
        elif args.command == "get":
            print_movie(client.get_movie(args.movie_id))
        elif args.command == "create":
            print_movie(
                client.create_movie(
                    title=args.title,
                    rating=args.rating,
                    comments_count=args.comments_count,
                    quote=args.quote,
                    url=args.url,
                )
            )
        elif args.command == "update":
            print_movie(
                client.update_movie(
                    args.movie_id,
                    title=args.title,
                    rating=args.rating,
                    comments_count=args.comments_count,
                    quote=args.quote,
                    url=args.url,
                )
            )
        elif args.command == "delete":
            print(client.delete_movie(args.movie_id).message)
        elif args.command == "clear":
            response = client.clear_movies()
            print(f"已清空，删除 {response.deleted_count} 条")
    finally:
        client.close()


if __name__ == "__main__":
    main()
