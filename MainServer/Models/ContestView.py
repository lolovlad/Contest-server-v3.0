from pydantic import BaseModel
from typing import List
from datetime import datetime
from .Compilations import GetCompilations


class ContestView(BaseModel):
    id: int
    datetime_start: datetime
    datetime_end: datetime
    datetime_registration: datetime = datetime.now()
    compiler: List[GetCompilations] = []

    class Config:
        orm_mode = True