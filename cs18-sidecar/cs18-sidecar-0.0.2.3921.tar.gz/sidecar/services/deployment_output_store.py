import json
import shlex
import threading
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import List

from sidecar.aws_session import AwsSession
from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const
from sidecar.model.objects import ISidecarConfiguration
from sidecar.services.deployment_output_converter import DeploymentOutputConverter


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

