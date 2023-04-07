import grpc
from grpc.aio import Channel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..tables import Contest, ContestRegistration

from fastapi import Depends

from ..Services.protos import contest_pb2, contest_pb2_grpc
from ..grps_review import get_channel
from ..Models.Contest import *
from typing import List, Any

from ..async_database import get_session
from json import loads


class ContestsRepository:
    def __init__(self,
                 channel: Channel = Depends(get_channel),
                 session: AsyncSession = Depends(get_session)):
        self.__channel: Channel = channel
        self.__session: AsyncSession = session

    async def get_list_report_total(self, id_contest: int) -> dict:
        sub = contest_pb2_grpc.ContestApiStub(self.__channel)
        request = contest_pb2.GetReportTotalRequest(id_contest=id_contest)
        response = await sub.GetReportTotal(request)
        result = loads(response.result.decode())
        return {key: TotalContest(**result[key]) for key in result}

    async def set_id_users(self, id_contest) -> List[int]:
        response = select(ContestRegistration.id_user).\
            distinct(ContestRegistration.id_user).\
            where(ContestRegistration.id_contest == id_contest)

        result = await self.__session.execute(response)
        return result.scalars().all()

    async def set_id_team(self, id_contest) -> List[int]:
        response = select(ContestRegistration.id_team). \
            distinct(ContestRegistration.id_team). \
            where(ContestRegistration.id_contest == id_contest)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_contest(self, id_contest: int) -> Contest:
        response = select(Contest).where(Contest.id == id_contest)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def update_user_state_contest(self,
                                        id_contest: int,
                                        id_user: int,
                                        state: int = 2):
        response = select(ContestRegistration).\
            where(ContestRegistration.id_contest == id_contest).\
            where(ContestRegistration.id_user == id_user)
        result = await self.__session.execute(response)
        result: ContestRegistration = result.scalars().first()
        result.state_contest = state
        await self.__session.commit()

    async def get_id_team_by_user_and_contest(self, id_user: int, id_contest: int):
        response = select(ContestRegistration.id_team).\
            where(ContestRegistration.id_user == id_user).\
            where(ContestRegistration.id_contest == id_contest)

        result = await self.__session.execute(response)
        return result.scalars().first() if len(result) > 0 else 0