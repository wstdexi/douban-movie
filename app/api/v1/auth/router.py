from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.controllers.auth_controller import auth_request_controller
from app.models.user import User
from app.schemas.login import CredentialsSchema, JWTOut, RegisterSchema
from app.schemas.auth import UserOut
from app.services.auth_service import auth_service

# 登录路由统一归类到 OpenAPI 的 auth 标签下。
router = APIRouter(prefix="/v1/auth", tags=["auth"])
_bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/register", response_model=JWTOut, summary="注册")
async def register(payload: RegisterSchema, db: Session = Depends(get_db)) -> JWTOut:
    try:
        auth_request_controller.validate_register_input(payload)
        return auth_service.register(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

# JSON 登录路由，返回 access token。
@router.post("/login", response_model=JWTOut, summary="登录")
async def login(credentials: CredentialsSchema, db: Session = Depends(get_db)) -> JWTOut:
    try:
        auth_request_controller.validate_login_input(credentials)
        return auth_service.login(db, credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/refresh", response_model=JWTOut, summary="刷新Token")
async def refresh_token(jwt_out: JWTOut, db: Session = Depends(get_db)) -> JWTOut:
    try:
        auth_request_controller.validate_refresh_input(jwt_out.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    try:
        return auth_service.refresh(db, jwt_out.refresh_token or "")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

@router.get("/me", response_model=UserOut, summary="获取当前用户信息")
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return auth_service.me(current_user)


@router.post("/logout", summary="退出登录")
async def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        auth_service.logout(credentials.credentials)
        return {"message": "logged out"}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc