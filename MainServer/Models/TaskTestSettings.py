from pydantic import BaseModel
from enum import Enum

from typing import List


class TypeTest(str, Enum):
    TEST = "test"
    MAIN = "main"


class CheckType(str, Enum):
    ONE = "one mistake"
    ALL = "many mistake"


class SettingsTest(BaseModel):
    limitation_variable: str
    necessary_test: str
    check_type: CheckType


class Test(BaseModel):
    score: int
    filling_type_variable: str
    answer: str



class ChunkTest(BaseModel):
    setting_tests: SettingsTest
    tests: List[Test]



class FileTaskTest(BaseModel):
    setting_tests: List[ChunkTest]