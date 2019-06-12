from abc import ABCMeta, abstractmethod
from typing import List


class DeploymentOutputsStore(metaclass=ABCMeta):

    @abstractmethod
    def save_application_outputs(self, app_name: str, app_instance_id: str, outputs: str):
        raise NotImplemented()

    @abstractmethod
    def save_service_outputs(self, service_name: str, outputs_json: {}):
        raise NotImplemented()

    @abstractmethod
    def get_deployment_outputs(self, outputs: List[str]) -> str:
        raise NotImplemented()

