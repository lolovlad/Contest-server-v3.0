from typing import List
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from ..tables import User, TeamRegistration
from ..Models.User import UserPost, UserUpdate, UserBase, UserGetInTeam, TeamUser, TypeUser, UserGet
from ..Models.Message import StatusUser

from ..Repositories.UserRepository import UserRepository
from ..Repositories.EduOrganizationRepository import EduOrganizationRepository


class UsersServices:
    def __init__(self,
                 user_repository: UserRepository = Depends(),
                 edu_repository: EduOrganizationRepository = Depends()):
        self.__repo: UserRepository = user_repository
        self.__repo_edu: EduOrganizationRepository = edu_repository
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

    async def get_list_user(self, number_page: int, type_user: str) -> List[UserGet]:
        offset = (number_page - 1) * self.__count_item
        users_entity = await self.__repo.get_list_user_by_user_type(offset, self.__count_item, type_user)
        users_models = [UserGet.model_validate(entity, from_attributes=True) for entity in users_entity]
        return users_models

    async def get_list_in_team_user(self, id_team: int) -> List[User]:
        users = await self.__repo.get_list_user_in_team(id_team)
        return users

    async def add_user(self, user_data: UserPost):
        if await self.__is_login(user_data):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
        user = User(**user_data.dict())

        edu_org = await self.__repo_edu.get_by_uuid(user_data.id_edu_organization)
        user.id_edu_organization = edu_org.id
        type_user = await self.__repo.get_type_user_by_id(user.id_type)
        if type_user.name == "admin":
            user.password = user_data.password
        else:
            user.hashed_password = user_data.password

        await self.__repo.add(user)

    async def update_user(self, id_user: int, user_data: UserUpdate):
        user = await self.__get(id_user)
        if user.type.name == "admin":
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)

        edu_org = await self.__repo_edu.get_by_uuid(user_data.id_edu_organization)

        for field, val in user_data:
            if field == "password":
                if len(val) > 0:
                    if user_data.type.name == "admin":
                        setattr(user, field, val)
                    else:
                        setattr(user, "hashed_password", val)
            elif field == "id_edu_organization":
                setattr(user, field, edu_org.id)
            else:
                setattr(user, field, val)
        await self.__repo.update(user)

    async def delete_user(self, id_user: int):
        user = await self.__get(id_user)
        if user.type.name == "admin":
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
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

    async def get_list_type_user(self) -> list[TypeUser]:
        list_type_user = await self.__repo.get_list_type_user()
        return [TypeUser.model_validate(i, from_attributes=True) for i in list_type_user]