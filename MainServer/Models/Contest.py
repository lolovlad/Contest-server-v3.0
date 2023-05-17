from pydantic import BaseModel
from datetime import datetime
from typing import List
from enum import Enum
from .Task import TaskGet


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


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

    class Config:
        json_encoders = {
            # custom output conversion for datetime
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }


class ContestGet(BaseContest):
    id: int
    datetime_start: datetime
    datetime_end: datetime
    description: str
    datetime_registration: datetime = datetime.now()
    users: List[UserContest]
    tasks: List[TaskGet]

    class Config:
        orm_mode = True


class ContestPost(BaseContest):
    datetime_start: str
    datetime_end: str
    description: str


class ContestPutUsers(BaseModel):
    id: int
    users: List[UserContest]


class ContestUpdate(BaseContest):
    id: int
    datetime_start: str
    datetime_end: str
    description: str


class ContestCardView(BaseContest):
    id: int
    is_view: bool


class TotalContest(BaseModel):
    name: int
    total: dict
    sum_point: int
    name_contest: str = ""
    description: str
    type_contest: TypeContest


class ResultContest(BaseModel):
    name_contest: str = ""
    type_contest: TypeContest = 1
    count_user: int = 0,
    count_task: int = 0,
    users: List[dict] = []

