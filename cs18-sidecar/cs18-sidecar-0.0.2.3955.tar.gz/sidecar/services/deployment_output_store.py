from abc import ABCMeta, abstractmethod
from typing import List


class DeploymentOutputStore(metaclass=ABCMeta):

    @abstractmethod
    def save_application_output(self, app_name: str, app_instance_id: str, output: str):
        raise NotImplemented()

    @abstractmethod
    def save_service_output(self, service_name: str, output_json: {}):
        raise NotImplemented()

    @abstractmethod
    def get_deployment_outputs(self, outputs: List[str]) -> str:
        raise NotImplemented()

