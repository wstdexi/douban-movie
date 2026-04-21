# 用户核心控制器：继承CRUDBase，封装用户相关数据库操作。

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.crud import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCoreCrud(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self) -> None:
        super().__init__(User)

    # 通过 username 或 email 查询用户。
    def get_by_identifier(self, db: Session, identifier: str) -> User | None:
        stmt = select(User).where(or_(User.username == identifier, User.email == identifier))
        return db.scalar(stmt)

    # 查询任意一个超级用户（用于初始化判断）。
    def get_any_superuser(self, db: Session) -> User | None:
        stmt = select(User).where(User.is_superuser.is_(True)).limit(1)
        return db.scalar(stmt)

    # 通过用户名查询。
    def get_by_username(self, db: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return db.scalar(stmt)

    # 通过邮箱查询。
    def get_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.scalar(stmt)


user_core_crud = UserCoreCrud()
# Backward-compatible alias used by existing modules.
user_core_controller = user_core_crud

