from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..async_database import get_session

from fastapi import Depends

from typing import List, Any


class TeamRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get_team(self, id_team: int):
       pass
