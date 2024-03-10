from typing import List
from enum import Enum
from pydantic import BaseModel, field_serializer
from pydantic import UUID4


class TypeOrganization(BaseModel):
    id: int
    name: str
    start_range: int
    end_range: int
    description: str
    postfix: str


class OrganizationBase(BaseModel):
    name_organizations: str
    type_organizations: TypeOrganization


class OrganizationViewGet(OrganizationBase):
    uuid: UUID4

    @field_serializer('uuid')
    def serialize_dt(self, dt: UUID4, _info):
        return str(dt)


class OrganizationGet(OrganizationBase):
    id: int


class OrganizationUpdate(OrganizationBase):
    id: int
