from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..tables import EducationalOrganizations
from ..Models.EducationalOrganizations import OrganizationBase, OrganizationUpdate, TypeOrganization
from ..Repositories.EduOrganizationRepository import EduOrganizationRepository


class EducationalOrganizationServices:
    def __init__(self, repo: EduOrganizationRepository = Depends()):
        self.__repo: EduOrganizationRepository = repo

    async def get_list_type_edu(self) -> list[TypeOrganization]:
        list_type_edu = await self.__repo.get_list_type_edu()
        return [TypeOrganization.model_validate(i, from_attributes=True) for i in list_type_edu]

    async def get_list_organizations(self) -> List[EducationalOrganizations]:
        list_organizations = await self.__repo.get_all_organizations()
        return list_organizations

    async def get_list_organizations_type(self, id_type_edu: int) -> List[EducationalOrganizations]:
        list_organizations = await self.__repo.get_all_organizations_by_type_org(id_type_edu)
        return list_organizations

    async def add_organization(self, edu_data: OrganizationBase):
        await self.__repo.add(edu_data)

    async def update_organization(self, edu_data: OrganizationUpdate):
        edu = await self.__repo.get(edu_data.id)
        for field, val in edu_data:
            setattr(edu, field, val)
        await self.__repo.update(edu)

    async def delete_organization(self, edu_id: int):
        await self.__repo.delete(edu_id)
