from pydantic import BaseModel, UUID4, field_serializer
from typing import List
from enum import Enum

from .TaskTestSettings import Test, SettingsTest


class TypeTask(BaseModel):
    id: int
    name: str
    description: str


class Complexity(int, Enum):
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
    name_task: str
    complexity: Complexity


class BaseGetTask(BaseTask):
    uuid: UUID4
    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class BaseTaskSettings(BaseModel):
    time_work: int = 1
    size_raw: int = 32
    type_input: TypeInput = 1
    type_output: TypeOutput = 1
    number_shipments: int = 100


class GetTaskSettings(BaseTaskSettings):
    files: List[str] = []


class TaskGet(BaseGetTask):
    type_task: TypeTask
    description: str
    description_input: str = None
    description_output: str = None


class TaskPost(BaseTask):
    id_type_task: int
    description: str
    description_input: str = None
    description_output: str = None


class TaskPut(BaseTask):
    description: str
    description_input: str = None
    description_output: str = None


class FileUpload(BaseModel):
    file_name: str
    file_extend: str
    file: object
    task: TaskGet


class TaskGetView(BaseGetTask):
    type_task: TypeTask


class TaskViewUser(TaskGetView):
    id: int
    last_answer: str = "-"

class GetListTaskViewUser(BaseModel):
    list_task: List[TaskViewUser]


class TaskAndTest(TaskGet, GetTaskSettings):
    view_settings: List[SettingsTest] = []
    view_test: List[Test] = []


class TaskToContest(BaseModel):
    task: TaskGetView
    in_contest: bool