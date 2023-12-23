from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..tables import User, ContestRegistration, TeamRegistration
from ..async_database import get_session
from ..Models.User import UserPost

from fastapi import Depends

from typing import List, Any

from ..Models.Message import TypeStatus


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self) -> int:
        response = select(func.count(User.id))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_user(self, id_user: int) -> User:
        result = await self.__session.get(User, id_user)
        return result

    async def state_user(self, id_contest: int, id_user: int) -> int:
        response = select(ContestRegistration.state_contest).\
            where(ContestRegistration.id_contest == id_contest).\
            where(ContestRegistration.id_user == id_user)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_list_user_by_user_type(self, start: int, limit: int, type_user: str) -> List[User]:
        if type_user == "all":
            response = select(User)
        elif type_user == "user":
            response = select(User).where(User.type == 2)
        else:
            response = select(User).where(User.type == 1)

        response = response.offset(start).fetch(limit).order_by(User.id)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()

    async def get_user_by_login(self, login: str) -> User:
        response = select(User).where(User.login == login)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_list_user_in_team(self, id_team: int) -> List[User]:
        response = select(User, TeamRegistration)\
            .join(User.teams)\
            .where(TeamRegistration.id_team != id_team)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, user: User):
        try:
            self.__session.add(user)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def update(self, user: User):
        try:
            self.__session.add(user)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete(self, user):
        try:
            await self.__session.delete(user)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def shit_response(self, type_user) -> List[User]:
        response = select(User).where(User.type != type_user)
        result = await self.__session.execute(response)
        return result.unique().scalars().all()