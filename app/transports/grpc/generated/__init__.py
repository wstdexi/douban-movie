from pathlib import Path
import sys

# grpcio-tools may generate `import movie_pb2` (top-level import) in
# `movie_pb2_grpc.py`. Ensure this directory is importable as a top-level
# module so container/runtime imports work without post-processing.
generated_dir = str(Path(__file__).resolve().parent)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir)

from app.transports.grpc.generated import movie_pb2, movie_pb2_grpc

__all__ = ["movie_pb2", "movie_pb2_grpc"]
