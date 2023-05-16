from typing import List
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from ..tables import User, TeamRegistration
from ..Models.User import UserPost, UserUpdate, UserBase, UserGetInTeam, TeamUser, TypeUser
from ..Models.Message import StatusUser

from ..Repositories.UserRepository import UserRepository


class UsersServices:
    def __init__(self,
                 user_repository: UserRepository = Depends()):
        self.__repo: UserRepository = user_repository
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    async def __get(self, id_user: int) -> User:
        user = await self.__repo.get_user(id_user)
        return user

    async def __is_login(self, user: UserBase) -> bool:
        users = await self.__repo.get_user_by_login(user.login)
        if users:
            return True
        return False

    async def get_count_page(self) -> int:
        count_row = await self.__repo.count_row()
        i = int(count_row % self.__count_item != 0)
        return count_row // self.__count_item + i

    async def get_user_id(self, id_user: int) -> User:
        return await self.__get(id_user)

    async def get_list_user(self, number_page: int, type_user: str) -> List[User]:
        offset = (number_page - 1) * self.__count_item
        users = await self.__repo.get_list_user_by_user_type(offset, self.__count_item, type_user)
        return users

    async def get_list_in_team_user(self, id_team: int) -> List[User]:
        users = await self.__repo.get_list_user_in_team(id_team)
        return users

    async def add_user(self, user_data: UserPost):
        if await self.__is_login(user_data):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
        user = User(**user_data.dict())
        if user.type == TypeUser.ADMIN:
            user.password = user_data.password
        else:
            user.hashed_password = user_data.password

        await self.__repo.add(user)

    async def update_user(self, id_user: int, user_data: UserUpdate):
        user = await self.__get(id_user)
        for field, val in user_data:
            if field == "password":
                if len(val) > 0:
                    if user_data.type == TypeUser.ADMIN:
                        setattr(user, field, val)
                    else:
                        setattr(user, "hashed_password", val)
            else:
                setattr(user, field, val)
        await self.__repo.update(user)

    async def delete_user(self, id_user: int):
        user = await self.__get(id_user)
        await self.__repo.delete(user)

    async def get_list_in_contest_user(self, id_contest: int) -> dict:
        users = await self.__repo.shit_response(TypeUser.ADMIN)
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

    async def status_user(self, id_contest: int, id_user: int) -> StatusUser:
        state = await self.__repo.state_user(id_contest, id_user)
        return StatusUser(**{"id_user": id_user, "status": state})

