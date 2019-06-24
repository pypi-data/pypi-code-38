from enum import Enum

from alas_ce0.common.client_base import EntityClientBase


class PackagePhysicalStatusType(Enum):
    Pending = 1
    Accepted = 2
    Damaged = 3
    Missing = 4


class PackageTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/package-templates/'