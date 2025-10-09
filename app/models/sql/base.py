import datetime as dt
import uuid
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column, registry

from app.utils.custom_types import Int64

auto_uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    ),
]
auto_int_pk = Annotated[Int64, mapped_column(primary_key=True, autoincrement=True)]


class Base(DeclarativeBase):
    __abstract__ = True
    registry = registry(
        type_annotation_map={
            Int64: BigInteger(),
            dt.datetime: DateTime(timezone=True),
        }
    )
