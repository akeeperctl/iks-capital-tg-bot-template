from typing import Annotated, NewType, TypeAlias

from pydantic import PlainValidator, Field

ListStr = NewType("ListStr", list[str])
StringList: TypeAlias = Annotated[ListStr, PlainValidator(func=lambda x: x.split(","))]

Int16: TypeAlias = Annotated[int, 16]
Int32: TypeAlias = Annotated[int, 32]
Int64: TypeAlias = Annotated[int, 64]

## Akeeper 16.10.2025
EntityId: TypeAlias = Annotated[int, Field]
Str2: TypeAlias = Annotated[str, Field(min_length=2)]
Str3: TypeAlias = Annotated[str, Field(min_length=3)]
Str5: TypeAlias = Annotated[str, Field(min_length=5)]
Str8: TypeAlias = Annotated[str, Field(min_length=8)]
## ~Akeeper
