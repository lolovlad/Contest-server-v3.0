from pydantic import BaseModel
from typing import List
from enum import Enum

from .TaskTestSettings import Test, SettingsTest


class TypeTask(int, Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    I = 5
    F = 6


class TypeInput(int, Enum):
    STREAM = 1
    FILE = 2


class TypeOutput(int, Enum):
    STREAM = 1
    FILE = 2


class BaseTask(BaseModel):
    id_contest: int
    name_task: str
    description: str
    description_input: str
    description_output: str
    type_task: TypeTask


class TaskSettings(BaseModel):
    id: int
    time_work: int
    size_raw: int
    type_input: TypeInput = 1
    type_output: TypeOutput = 1
    number_shipments: int
    files: List[str] = []


class TaskGet(BaseTask):
    id: int

    class Config:
        orm_mode = True


class TaskPost(BaseTask):
    pass


class TaskPut(BaseTask):
    id: int


class FileUpload(BaseModel):
    file_name: str
    file_extend: str
    file: object
    task: TaskGet


class TaskGetView(BaseModel):
    id: int
    name_task: str
    type_task: TypeTask

    class Config:
        orm_mode = True


class TaskViewUser(TaskGetView):
    last_answer: str = "-"

    class Config:
        orm_mode = True


class GetListTaskViewUser(BaseModel):
    list_task: List[TaskViewUser]


class TaskAndTest(TaskGet, TaskSettings):
    view_settings: List[SettingsTest] = []
    view_test: List[Test] = []