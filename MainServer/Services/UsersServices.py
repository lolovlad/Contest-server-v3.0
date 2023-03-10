from typing import List
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import lazyload

from ..tables import User, TeamRegistration
''', TeamRegistration, ContestRegistration'''
from ..Models.User import UserPost, UserUpdate, UserBase, UserGetInTeam, TeamUser, TypeUser
from ..Models.Message import StatusUser
from ..database import get_session


class UsersServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session: Session = session

    def __get(self, id_user: int):
        user = self.__session.query(User).filter(User.id == id_user).first()
        return user

    def __is_login(self, user: UserBase):
        users = self.__session.query(User).filter(User.login == user.login).first()
        if users:
            return True
        return False

    def get_user_id(self, id_user: int) -> User:
        return self.__get(id_user)

    def get_list_user(self, type_user: str) -> List[User]:
        if type_user == "all":
            return self.__session.query(User).all()
        elif type_user == "user":
            return self.__session.query(User).filter(User.type == 2).all()
        return self.__session.query(User).filter(User.type == 1).all()

    def get_list_in_team_user(self, id_team: int) -> List[User]:
        users = self.__session.execute(select(User, TeamRegistration).join(User.teams).where(TeamRegistration.id_team != id_team))
        target_user = []
        for user in users.scalars():
            target_user.append(user)
        return target_user

    def add_user(self, user_data: UserPost) -> User:
        if self.__is_login(user_data):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
        user = User(**user_data.dict())
        if user.type == TypeUser.ADMIN:
            user.password = user_data.password
        else:
            user.hashed_password = user_data.password
        self.__session.add(user)
        self.__session.commit()
        return user

    def update_user(self, id_user: int, user_data: UserUpdate) -> User:
        user = self.__get(id_user)
        for field, val in user_data:
            if field == "password":
                if len(val) > 0:
                    if user_data.type == TypeUser.ADMIN:
                        setattr(user, field, val)
                    else:
                        setattr(user, "hashed_password", val)
            else:
                setattr(user, field, val)
        self.__session.commit()
        return user

    def delete_user(self, id_user: int):
        user = self.__get(id_user)
        self.__session.delete(user)
        self.__session.commit()
        return user

    def get_list_in_contest_user(self, id_contest: int) -> dict:
        users = self.__session.query(User).filter(User.type != TypeUser.ADMIN).all()
        users_reg = []
        users_not_reg = []
        for user in users:
            id_contests = list(map(lambda x: x.id_contest, user.contests))
            teams = list(map(lambda x: TeamUser(id=x.team.id,
                                                name_team=x.team.name_team), user.teams))
            target_user = UserGetInTeam(id=user.id,
                                        name=user.name,
                                        sename=user.sename,
                                        secondname=user.secondname,
                                        teams=teams)
            if id_contest in id_contests:
                users_reg.append(target_user)
            else:
                users_not_reg.append(target_user)
        return {
            "user_in_contest": users_reg,
            "user_not_in_contest": users_not_reg
        }


    def status_user(self, id_contest: int, id_user: int) -> StatusUser:
        contest = self.__session.query(ContestRegistration).filter(ContestRegistration.id_contest == id_contest)\
            .filter(ContestRegistration.id_user == id_user).first()
        return StatusUser(**{"id_user": id_user, "status": contest.state_contest})

