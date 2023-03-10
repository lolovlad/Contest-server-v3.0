from fastapi import APIRouter, Depends

from typing import List

from ..Models.Team import TeamGet, TeamPost, TeamDelete, TeamsContest
from ..Models.User import UserGet, TypeUser
from ..Services.LoginServices import get_current_user
from ..Services.TeamsServices import TeamsServices


router = APIRouter(prefix="/teams")


@router.get("/", response_model=List[TeamGet])
def get_team(team_services: TeamsServices = Depends()):
    return team_services.get_list_team()


@router.get("/{id_team}", response_model=TeamGet)
def get_one_team(id_team: int, team_services: TeamsServices = Depends()):
    return team_services.get_team(id_team)


@router.post("/", response_model=TeamGet)
def post_team(team_data: TeamPost, team_services: TeamsServices = Depends(),
              user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        print(team_data, "--------------")
        return team_services.add_team(team_data)


@router.put("/", response_model=TeamGet)
def put_team(team_data: TeamGet, team_services: TeamsServices = Depends(),
             user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        return team_services.update_team(team_data)


@router.delete("/{id_team}", response_model=TeamDelete)
def delete_team(id_team: int, team_services: TeamsServices = Depends(),
                user: UserGet = Depends(get_current_user)):
    if user.type == TypeUser.ADMIN:
        return team_services.delete_team(id_team)


@router.get("/in_contest/{id_contest}", response_model=TeamsContest)
def get_list_team_in_contest(id_contest: int, team_services: TeamsServices = Depends()):
    return team_services.get_list_team_in_contest(id_contest)
