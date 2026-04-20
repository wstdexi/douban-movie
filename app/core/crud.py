from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

# SQLAlchemy 模型类型。
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# 通用CRUD基类（SQLAlchemy版本）。
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    # 通过ID查询。
    def get(self, db: Session, id: int) -> ModelType | None:
        return db.get(self.model, id)

    # 创建数据。
    def create(self, db: Session, *, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()
        obj = self.model(**obj_data)  # type: ignore[call-arg]
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    # 更新数据。
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # 删除数据。
    def remove(self, db: Session, *, id: int) -> ModelType | None:
        obj = self.get(db, id=id)
        if obj is None:
            return None
        db.delete(obj)
        db.commit()
        return obj