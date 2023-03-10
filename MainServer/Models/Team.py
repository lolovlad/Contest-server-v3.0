from pydantic import BaseModel
from typing import List


class UserTeam(BaseModel):
    id: int
    name: str
    sename: str
    secondname: str
    id_team: int = 0


class BaseTeam(BaseModel):
    name_team: str


class TeamGet(BaseTeam):
    id: int
    users: List[UserTeam]

    class Config:
        orm_mode = True


class TeamPost(BaseTeam):
    users: List[UserTeam]


class TeamDelete(BaseTeam):
    id: int


class TeamsContest(BaseModel):
    team_in_contest: List[TeamGet]
    team_not_in_contest: List[TeamGet]