from pydantic import BaseModel, UUID4, field_serializer
from datetime import datetime
from typing import List
from enum import Enum
from .Task import TaskGetView
from .User import UserGet


class StateUserInContest(int, Enum):
    WORKS = 1
    BANNED = 2
    FINISHED = 3


class UserContest(BaseModel):
    pass


class TypeContest(BaseModel):
    id: int
    name: str
    description: str


class StateContest(BaseModel):
    id: int
    name: str
    description: str


class BaseContest(BaseModel):
    name_contest: str


class BaseGetContest(BaseContest):
    uuid: UUID4
    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class ContestGet(BaseGetContest):
    datetime_start: datetime
    datetime_end: datetime
    description: str
    datetime_registration: datetime = datetime.now()
    type: TypeContest
    state_contest: StateContest
    #users: list[] = None
    #tasks: list[] = None


class ContestCardView(BaseGetContest):
    type: TypeContest
    state_contest: StateContest
    datetime_start: datetime
    datetime_end: datetime


class ContestUserMenu(BaseModel):
    contest: ContestCardView
    is_view: bool


class ContestPost(BaseContest):
    datetime_start: str
    datetime_end: str
    description: str
    id_type: int
    id_state_contest: int


class ContestPutUsers(BaseModel):
    id: int
    #users: List[UserContest]


class ContestUpdate(BaseContest):
    datetime_start: str
    datetime_end: str
    description: str


class TotalContest(BaseModel):
    name: int
    total: dict
    sum_point: int
    name_contest: str = ""


class ResultContest(BaseModel):
    name_contest: str = ""
    type_contest: TypeContest = 1
    count_user: int = 0,
    count_task: int = 0,
    rows: list[dict] = []


class ContestToTask(BaseModel):
    uuid_task: str
    uuid_contest: str


class ContestToUser(BaseModel):
    id_user: int
    id_contest: int
    state_contest: StateUserInContest


class ContestToUserAdd(BaseModel):
    id_user: int
    uuid_contest: str


class ContestUserAndTask(BaseGetContest):
    type: TypeContest
    state_contest: StateContest
    datetime_start: datetime
    datetime_end: datetime
    users: list[UserGet]
    tasks: list[TaskGetView]