# PythonProject4

基于 FastAPI + SQLAlchemy + PostgreSQL 的学习项目，包含：

- 电影 CRUD 接口（`/movies`）
- JWT 登录与鉴权（`/v1/auth/login`、`/v1/auth/refresh`、`/v1/auth/me`）
- 初始化脚本（建表、创建超级用户、抓取豆瓣 Top250 数据）

## 1. 环境要求

- Python 3.12+
- PostgreSQL 13+
- `uv`（推荐）

## 2. 安装依赖

在项目根目录执行：

```bash
uv sync
```

如果访问 pypi.org 较慢，可使用镜像：

```bash
UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple uv sync
```

## 3. 配置环境变量

复制模板文件并按需修改：

```bash
cp .env.example .env
```

## 4. 初始化数据

执行初始化脚本（会做以下事情）：

1. 初始化数据库结构（Alembic 开关由 `RUN_ALEMBIC_UPGRADE` 控制）
2. 根据配置创建超级用户（如果不存在）
3. 抓取并写入豆瓣电影数据

```bash
python app/init_data.py
```

## 5. 启动服务

```bash
python app/main.py
```

启动后访问：

- Swagger 文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 6. 最小接口验收清单

### 6.1 登录获取 token

- 接口：`POST /v1/auth/login`
- 请求体：

```json
{
  "username": "admin",
  "password": "请替换为你的 SUPERUSER_PASSWORD"
}
```

- 预期：返回 `token` 和 `refreshToken`

### 6.2 使用 access token 获取当前用户

- 接口：`GET /v1/auth/me`
- 头部：
  - `Authorization: Bearer <token>`
- 预期：返回当前用户信息

### 6.3 新增电影

- 接口：`POST /movies`
- 请求体示例：

```json
{
  "title": "Demo Movie",
  "rating": 8.8,
  "comments_count": 1234,
  "quote": "hello",
  "url": "https://example.com/demo-movie"
}
```

- 预期：返回新增后的电影对象

### 6.4 查询电影列表

- 接口：`GET /movies?skip=0&limit=20`
- 预期：返回电影列表

## 7. 常见问题

- 若登录失败，请确认：
  - 已执行 `python app/init_data.py`
  - `.env` 中 `SUPERUSER_PASSWORD` 与登录密码一致
- 若数据库连接失败，请确认：
  - PostgreSQL 已启动
  - `.env` 中 `POSTGRES_*` 配置正确
