from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import AppInstanceIdentifier


class StaleAppInstanceException(Exception):
    pass


class IAppInstanceService:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_status_if_not_stale(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        raise NotImplementedError

    @abstractmethod
    def check_which_exist(self, identifiers: List[AppInstanceIdentifier]) -> List[AppInstanceIdentifier]:
        raise NotImplementedError

    @abstractmethod
    def get_public_address(self, app_instance_identifier: AppInstanceIdentifier) -> str:
        raise NotImplementedError
