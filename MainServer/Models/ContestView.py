from pydantic import BaseModel, UUID4, field_serializer
from typing import List
from datetime import datetime
from .Compilations import GetCompilations


class ContestView(BaseModel):
    uuid: UUID4
    name_contest: str
    datetime_start: datetime
    datetime_end: datetime
    datetime_registration: datetime = datetime.now()
    compiler: List[GetCompilations] = []

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)
