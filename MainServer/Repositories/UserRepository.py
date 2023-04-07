from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..tables import User, ContestRegistration
from ..async_database import get_session

from fastapi import Depends

from typing import List, Any

from ..Models.Message import TypeStatus


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get_user(self, id_user: int) -> User:
        result = await self.__session.get(User, id_user)
        return result

    async def state_user(self, id_contest: int, id_user: int) -> int:
        response = select(ContestRegistration.state_contest).\
            where(ContestRegistration.id_contest == id_contest).\
            where(ContestRegistration.id_user == id_user)
        result = await self.__session.execute(response)
        return result.scalars().first()