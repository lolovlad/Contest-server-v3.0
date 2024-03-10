from fastapi import APIRouter, Depends
from typing import List

from ..Models.EducationalOrganizations import OrganizationBase, OrganizationViewGet, OrganizationUpdate, TypeOrganization
from ..Services.EducationalOrganizationServices import EducationalOrganizationServices

router = APIRouter(prefix='/educational_organizations')


@router.get('/type_edu/', response_model=list[TypeOrganization])
async def get_list_type_edu(edu_services: EducationalOrganizationServices = Depends()):
    list_type_edu = await edu_services.get_list_type_edu()
    return list_type_edu


@router.get('/', response_model=List[OrganizationViewGet])
async def get_organizations(edu_services: EducationalOrganizationServices = Depends()):
    list_organization = await edu_services.get_list_organizations()
    return list_organization


@router.get('/by_type/{id_type_edu}', response_model=List[OrganizationViewGet])
async def get_organizations_type(id_type_edu: int,
                                 edu_services: EducationalOrganizationServices = Depends()):
    list_organization = await edu_services.get_list_organizations_type(id_type_edu)
    return list_organization


@router.post('/', response_model=OrganizationViewGet)
async def post_organization(edu_services: EducationalOrganizationServices = Depends(),
                            edu: OrganizationBase = None):
    await edu_services.add_organization(edu)


@router.put('/', response_model=OrganizationViewGet)
async def put_organization(edu: OrganizationUpdate,
                           edu_services: EducationalOrganizationServices = Depends()):
    await edu_services.update_organization(edu)


@router.delete('/{edu_id}')
async def delete_organization(edu_id: int,
                              edu_services: EducationalOrganizationServices = Depends()):
    await edu_services.delete_organization(edu_id)