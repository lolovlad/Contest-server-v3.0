from pydantic import BaseModel
from datetime import datetime
from typing import List
from enum import Enum
from .Task import TaskGet


class TypeContest(int, Enum):
    OLIMPIADA = 1
    TEAM_OLIMPIADA = 2
    HACKATHON = 3


class TypeState(int, Enum):
    REGISTERED = 0
    CONFIRMED = 1
    GOING_ON = 2
    FINISHED = 3


class UserContest(BaseModel):
    id: int
    sename: str
    name: str
    secondname: str
    id_team: int = 0


class BaseContest(BaseModel):
    name_contest: str
    type: TypeContest = 1

    state_contest: TypeState = 0


class ContestGet(BaseContest):
    id: int
    datetime_start: datetime
    datetime_end: datetime
    datetime_registration: datetime = datetime.now()
    users: List[UserContest]
    tasks: List[TaskGet]

    class Config:
        orm_mode = True


class ContestPost(BaseContest):
    datetime_start: str
    datetime_end: str


class ContestDelete(BaseContest):
    id: int


class ContestPutUsers(BaseModel):
    id: int
    users: List[UserContest]


class ContestUpdate(BaseContest):
    id: int
    datetime_start: str
    datetime_end: str


class ContestCardView(BaseContest):
    id: int
    is_view: bool

'''
class ContestGetPage(BaseContest):
    id: int
    tasks: List[TaskPage]

    class Config:
        orm_mode = True
'''
