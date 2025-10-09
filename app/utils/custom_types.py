from typing import Annotated, NewType, TypeAlias

from pydantic import PlainValidator

ListStr = NewType("ListStr", list[str])
StringList: TypeAlias = Annotated[ListStr, PlainValidator(func=lambda x: x.split(","))]

Int16: TypeAlias = Annotated[int, 16]
Int32: TypeAlias = Annotated[int, 32]
Int64: TypeAlias = Annotated[int, 64]
