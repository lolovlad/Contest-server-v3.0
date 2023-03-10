from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from ..tables import EducationalOrganizations
from ..Models.EducationalOrganizations import OrganizationBase, OrganizationUpdate
from ..database import get_session


class EducationalOrganizationServices:
    def __init__(self, session: Session = Depends(get_session)):
        self.__session = session

    def __get(self, id_edu) -> EducationalOrganizations:
        return self.__session.query(EducationalOrganizations).filter(EducationalOrganizations.id == id_edu).first()

    def get_list_organizations(self) -> List[EducationalOrganizations]:
        return self.__session.query(EducationalOrganizations).all()

    def get_list_organizations_type(self, type_org: int) -> List[EducationalOrganizations]:
        return self.__session.query(EducationalOrganizations).filter(EducationalOrganizations.type_organizations == type_org).all()

    def add_organization(self, edu_data: OrganizationBase) -> EducationalOrganizations:
        edu = EducationalOrganizations(**edu_data.dict())
        self.__session.add(edu)
        self.__session.commit()
        return edu

    def update_organization(self, edu_data: OrganizationUpdate) -> EducationalOrganizations:
        edu = self.__get(edu_data.id)
        for field, val in edu_data:
            setattr(edu, field, val)
        self.__session.commit()
        return edu

    def delete_organization(self, edu_id: int) -> EducationalOrganizations:
        edu = self.__get(edu_id)
        self.__session.delete(edu)
        self.__session.commit()
        return edu
