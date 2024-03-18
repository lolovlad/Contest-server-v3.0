from typing import List
from pydantic import BaseModel


class BaseCompilations(BaseModel):
    name: str
    extend: str


class GetCompilations(BaseCompilations):
    id: int


class GetNewCompilation(BaseModel):
    id: int
    name_compilation: str
    extension: str