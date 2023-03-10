from pydantic import BaseModel
from typing import List
from ..Models.Contest import TypeContest


class ReportTotal(BaseModel):
    name_contest: str
    type_contest: TypeContest
    name: str
    total: dict
    sum_point: int
