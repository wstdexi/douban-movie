# 认证模块路由文件（预留，待实现）。
from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@auth_router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(sub=str(user.id))
    return Token(access_token=access_token)