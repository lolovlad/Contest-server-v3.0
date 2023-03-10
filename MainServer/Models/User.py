from typing import List
from enum import Enum
from pydantic import BaseModel


class StateUser(int, Enum):
    NOTBANNED = 1
    BANNED = 2


class TeamUser(BaseModel):
    id: int
    name_team: str


class TypeUser(int, Enum):
    ADMIN = 1
    USER = 2


class UserBase(BaseModel):
    login: str
    type: TypeUser
    name: str
    sename: str
    secondname: str
    foto: str = "Photo/default.png"
    data: dict = {}


class UserGet(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserPost(UserBase):
    password: str


class UserUpdate(UserBase):
    id: int
    password: str


class UserGetInTeam(BaseModel):
    id: int
    name: str
    sename: str
    secondname: str
    teams: List[TeamUser]