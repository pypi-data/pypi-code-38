from datacore.datacore_restlike import Access as Access
from datacore.datacore_restlike import Endpoints as Endpoints
from datacore.datacore_restlike import DatacoreException as DatacoreException


Endpoints = Endpoints
Access = Access
DatacoreException = DatacoreException

__all__ = [
    "Access",
    "DatacoreException",
    "datacore_restlike",
    "types",
    ]