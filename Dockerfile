FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    alembic \
    requests \
    beautifulsoup4 \
    lxml \
    grpcio \
    grpcio-tools \
    pydantic

CMD ["python", "-m", "app.transports.grpc.server"]
