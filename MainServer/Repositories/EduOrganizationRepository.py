from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..async_database import get_session
from ..tables import EducationalOrganizations, TypeOrganizations
from ..Models.EducationalOrganizations import OrganizationBase


class EduOrganizationRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get(self, id_edu: int) -> EducationalOrganizations | None:
        entity = await self.__session.get(EducationalOrganizations, id_edu)
        return entity

    async def get_by_uuid(self, uuid_edu: str) -> EducationalOrganizations | None:
        query = select(EducationalOrganizations).where(EducationalOrganizations.uuid == uuid_edu)
        response = await self.__session.execute(query)
        return response.scalars().one_or_none()

    async def get_all_organizations(self) -> list[EducationalOrganizations]:
        query = select(EducationalOrganizations)
        response = await self.__session.execute(query)
        return response.scalars().all()

    async def get_all_organizations_by_type_org(self, type_org: int) -> list[EducationalOrganizations]:
        query = select(EducationalOrganizations).where(EducationalOrganizations.type_organizations_id == type_org)
        response = await self.__session.execute(query)
        return response.scalars().all()

    async def add(self, edu_data: OrganizationBase):
        entity = EducationalOrganizations(**edu_data.model_dump())
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()

    async def update(self, edu: EducationalOrganizations):
        try:
            self.__session.add(edu)
            await self.__session.commit()
        except:
            await self.__session.rollback()

    async def delete(self, id_edu: int):
        try:
            entity = await self.get(id_edu)
            await self.__session.delete(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()

    async def get_type_edu_by_uuid(self, uuid_type: str) -> TypeOrganizations | None:
        query = select(TypeOrganizations).where(TypeOrganizations.uuid == uuid_type)
        response = await self.__session.execute(query)
        return response.scalars().one_or_none()

    async def get_list_type_edu(self) -> list[TypeOrganizations]:
        query = select(TypeOrganizations)
        response = await self.__session.execute(query)
        return response.scalars().all()