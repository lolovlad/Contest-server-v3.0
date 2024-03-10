from pydantic import BaseModel
from typing import List
from datetime import datetime
from .Compilations import GetCompilations


class ContestView(BaseModel):
    id: int
    name_contest: str
    datetime_start: datetime
    datetime_end: datetime
    datetime_registration: datetime = datetime.now()
    compiler: List[GetCompilations] = []
