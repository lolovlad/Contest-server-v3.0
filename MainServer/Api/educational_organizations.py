from fastapi import APIRouter, Depends
from typing import List

from ..Models.EducationalOrganizations import OrganizationBase, OrganizationGet, OrganizationUpdate
from ..Services.EducationalOrganizationServices import EducationalOrganizationServices

router = APIRouter(prefix='/educational_organizations')


@router.get('/', response_model=List[OrganizationGet])
def get_organizations(edu_services: EducationalOrganizationServices = Depends()):
    return edu_services.get_list_organizations()


@router.get('/{type_edu}', response_model=List[OrganizationGet])
def get_organizations_type(type_edu: int,
                           edu_services: EducationalOrganizationServices = Depends()):
    return edu_services.get_list_organizations_type(type_edu)


@router.post('/', response_model=OrganizationGet)
def post_organization(edu_services: EducationalOrganizationServices = Depends(),
                      edu: OrganizationBase = None):
    return edu_services.add_organization(edu)


@router.put('/', response_model=OrganizationGet)
def put_organization(edu: OrganizationUpdate,
                     edu_services: EducationalOrganizationServices = Depends()):
    return edu_services.update_organization(edu)


@router.delete('/{edu_id}', response_model=OrganizationGet)
def delete_organization(edu_id: int,
                        edu_services: EducationalOrganizationServices = Depends()):
    return edu_services.delete_organization(edu_id)