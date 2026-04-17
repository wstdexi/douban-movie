import typing as t

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr

metadata = MetaData()
class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry, metadata=metadata)
class Base:
    metadata = metadata
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


__all__ = ["Base", "metadata"]
