from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..tables import Contest, ContestRegistration

from fastapi import Depends

from ..review_service import get_channel
from ..Models.Contest import *
from typing import List, Any

from ..async_database import get_session
from json import loads


class ContestsRepository:
    def __init__(self,
                 client: AsyncClient = Depends(get_channel),
                 session: AsyncSession = Depends(get_session)):
        self.__client: AsyncClient = client
        self.__session: AsyncSession = session

    async def __get_reg_users(self, id_contest: int) -> List[ContestRegistration]:
        response = select(ContestRegistration).where(ContestRegistration.id_contest == id_contest)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_list_report_total(self, id_contest: int) -> dict:
        response = await self.__client.get(f"contest/get_report/{id_contest}")
        result = loads(response.text)
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
        result = await self.__session.get(Contest, id_contest)
        return result.scalars()

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
        id_team = result.scalars().all()
        await self.__session.close()
        return id_team[0] if id_team[0] is not None else 0

    async def get_admin_panel_view_contest(self) -> list:
        response = select([Contest.id, Contest.state_contest, Contest.name_contest, Contest.type]).order_by(Contest.id)

        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_list_contest(self) -> List[Contest]:
        response = select(Contest)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, contest: Contest):
        try:
            self.__session.add(contest)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete(self, contest: Contest):
        try:
            await self.__session.delete(contest)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def update(self, contest: Contest):
        try:
            self.__session.add(contest)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()
            raise Exception

    async def add_users_contest(self, contest_data: ContestPutUsers):
        contest = await self.get_contest(contest_data.id)
        users = await self.__get_reg_users(contest_data.id)
        for user in users:
            await self.__session.delete(user)
        for user in contest_data.users:
            if user.id_team == 0:
                user.id_team = None
            contest_reg = ContestRegistration(id_user=user.id,
                                              id_contest=contest.id,
                                              id_team=user.id_team)
            self.__session.add(contest_reg)
        await self.__session.commit()

    async def get_contest_registration(self, id_user: int) -> list[ContestRegistration]:
        query = select(ContestRegistration).where(ContestRegistration.id_user == id_user)
        response = await self.__session.execute(query)
        return response.scalars().all()