from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..tables import Team, TeamRegistration, User
from ..Models.Team import UserTeam, TeamGet, TeamPost, TeamDelete
from ..Repositories.TeamRepository import TeamRepository


class TeamsServices:
    def __init__(self, repo: TeamRepository = Depends()):
        self.__repo: TeamRepository = repo

    def __get(self, id_team: int) -> Team:
        team = self.__session.query(Team).filter(Team.id == id_team).first()
        return team

    def __convert_team(self, id_team: int) -> TeamGet:
        team = self.__get(id_team)
        users = list(map(lambda x: UserTeam(id=x.user.id,
                                            name=x.user.name,
                                            sename=x.user.sename,
                                            secondname=x.user.secondname), team.users))
        teams_reg = TeamGet(id=team.id,
                            users=users,
                            name_team=team.name_team)
        return teams_reg

    def __get_reg_users(self, id_team: int) -> List[TeamRegistration]:
        users = self.__session.query(TeamRegistration).filter(TeamRegistration.id_team == id_team).all()
        return users

    def get_team(self, id_team: int) -> TeamGet:
        team = self.__convert_team(id_team)
        return team

    def get_list_team(self) -> List[TeamGet]:
        teams = self.__session.query(Team).all()
        teams_reg = []
        for team in teams:
            users = list(map(lambda x: UserTeam(id=x.user.id,
                                                name=x.user.name,
                                                sename=x.user.sename,
                                                secondname=x.user.secondname), team.users))
            teams_reg.append(TeamGet(id=team.id,
                                     users=users,
                                     name_team=team.name_team))
        return teams_reg

    def add_team(self, team_data: TeamPost) -> TeamGet:
        team = Team(name_team=team_data.name_team)

        self.__session.add(team)
        self.__session.commit()
        for user in team_data.users:
            team_reg = TeamRegistration(id_user=user.id,
                                        id_team=team.id)
            self.__session.add(team_reg)
        self.__session.commit()
        team = self.__convert_team(team.id)
        return team

    def update_team(self, team_data: TeamGet) -> TeamGet:
        team = self.__get(team_data.id)
        users = self.__get_reg_users(team_data.id)
        for user in users:
            self.__session.delete(user)

        for field, val in team_data:
            if field in ("name_team", "is_solo"):
                setattr(team, field, val)
        for user in team_data.users:
            team_reg = TeamRegistration(id_user=user.id,
                                        id_team=team.id)
            self.__session.add(team_reg)

        self.__session.commit()
        team = self.__convert_team(team.id)
        return team

    def delete_team(self, id_team: int) -> TeamDelete:
        team = self.__get(id_team)
        self.__session.delete(team)
        self.__session.commit()

        team = TeamDelete(id=team.id,
                          name_team=team.name_team)
        return team

    def get_list_team_in_contest(self, id_contest: int) -> dict:
        teams = self.__session.query(Team).all()
        teams_reg = []
        teams_not_reg = []
        for team in teams:
            id_contests = list(map(lambda x: x.id_contest, team.contests))
            users = list(map(lambda x: UserTeam(id=x.user.id,
                                                name=x.user.name,
                                                sename=x.user.sename,
                                                secondname=x.user.secondname,
                                                id_team=team.id), team.users))
            team_target = TeamGet(id=team.id,
                                  users=users,
                                  name_team=team.name_team)
            if id_contest not in id_contests:
                teams_reg.append(team_target)
            else:
                teams_not_reg.append(team_target)
        return {
            "team_in_contest": teams_not_reg,
            "team_not_in_contest": teams_reg
        }

