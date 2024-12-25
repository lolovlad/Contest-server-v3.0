from pydantic import BaseModel
from .Compilations import GetNewCompilation
from datetime import datetime


class AnswerGet(BaseModel):
    date_send: datetime
    id: int
    id_user: int
    id_task: int
    id_contest: int
    name_compilation: str
    total: str
    time: str
    memory_size: str
    number_test: int
    points: int


class AnswerView(BaseModel):
    date_send: datetime
    id: int
    name_user: str
    name_task: str
    name_compilation: str
    total: str
    time: str
    memory_size: str
    number_test: int
    points: int


class Report(BaseModel):
    report: dict


class GetAnswerNew(BaseModel):
    date_send: datetime
    id: int
    id_team: int
    id_user: int
    id_task: int
    id_contest: int
    compilation: GetNewCompilation
    total: str
    time: str
    memory_size: float
    number_test: int
    points: int


class AnswerReview(BaseModel):
    date_send: datetime
    id: int
    compilation: GetNewCompilation
    total: str
    time: str
    memory_size: float
    number_test: int
    points: int
    file_answer: str = ""


class PutPointAnswer(BaseModel):
    points: int
