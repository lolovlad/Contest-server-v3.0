from typing import List
from enum import Enum
from pydantic import BaseModel
from ..Models.EducationalOrganizations import OrganizationViewGet


class StateUser(int, Enum):
    NOTBANNED = 1
    BANNED = 2


class TeamUser(BaseModel):
    id: int
    name_team: str


class TypeUser(BaseModel):
    id: int
    name: str
    description: str


class UserBase(BaseModel):
    login: str
    name: str
    sename: str
    secondname: str
    foto: str = "Photo/default.png"
    stage_edu: str = None
    data: dict = {}


class UserGet(UserBase):
    id: int
    type: TypeUser
    edu_organization: OrganizationViewGet = None


class UserPost(UserBase):
    password: str
    id_type: int
    id_edu_organization: str


class UserUpdate(UserBase):
    password: str
    id_type: int
    id_edu_organization: str


class UserGetInTeam(BaseModel):
    id: int
    name: str
    sename: str
    secondname: str
    teams: List[TeamUser]


class UserToContest(BaseModel):
    user: UserGet
    in_contest: bool
