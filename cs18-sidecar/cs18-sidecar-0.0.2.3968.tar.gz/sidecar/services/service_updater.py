import json
import threading
from abc import ABCMeta, abstractmethod
from logging import Logger

from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.azure_clp.azure_status_maintainer import AzureStatusMaintainer
from sidecar.const import Const
from sidecar.kub_api_pod_reader import KubApiPodReader
from sidecar.kub_api_service import IKubApiService
from sidecar.services.service_status_state import ServiceStatusState
from sidecar.utils import Utils, CallsLogger


class IServiceUpdater(metaclass=ABCMeta):
    def __init__(self, service_status_state: ServiceStatusState, logger: Logger):
        self.service_status_state = service_status_state
        self.logger = logger
        self.lock = threading.RLock()

    @CallsLogger.wrap
    def update_status(self, name: str, status: str):
        self.on_update_status(name=name, status=status)
        self.service_status_state.update_status(name=name, status=status)

    @abstractmethod
    def on_update_status(self, name: str, status: str):
        raise NotImplemented()

    @abstractmethod
    def update_deployment_outputs(self, service_name: str, outputs: {}):
        raise NotImplemented()

    @abstractmethod
    def get_deployment_outputs(self, service_name: str) -> {}:
        raise NotImplemented()


class K8SServiceUpdater(IServiceUpdater):

    def __init__(self, kub_api_service: IKubApiService, service_status_state: ServiceStatusState, logger: Logger):
        super().__init__(service_status_state, logger)
        self._k8s_service = kub_api_service

    @staticmethod
    def _can_update_pod(pod):
        return pod and not KubApiPodReader.is_pod_ended(pod) and not KubApiPodReader.is_pod_terminating(pod)

    @CallsLogger.wrap
    def on_update_status(self, name: str, status: str):
        with self.lock:
            pod = self._get_pod()
            if self._can_update_pod(pod):
                service_data = KubApiPodReader.get_service_json(pod, name)
                service_data["status"] = status
                annotation_change = {name: json.dumps(service_data)}
                self._k8s_service.update_pod(Const.SERVICE_EXECUTION_POD, annotation_change)

    def _get_pod(self):
        pod = Utils.retry_on_exception(
            func=lambda: self._k8s_service.get_pod_by_name(name=Const.SERVICE_EXECUTION_POD),
            logger=self.logger,
            logger_msg="trying to get service execution pod")
        return pod

    def update_deployment_outputs(self, service_name: str, outputs: {}):
        with self.lock:
            pod = self._get_pod()
            if self._can_update_pod(pod):
                service_data = KubApiPodReader.get_service_json(pod, service_name)
                service_data["outputs"] = outputs
                annotation_change = {service_name: json.dumps(service_data)}
                self._k8s_service.update_pod(Const.SERVICE_EXECUTION_POD, annotation_change)

    def get_deployment_outputs(self, service_name: str) -> {}:
        pod = self._get_pod()
        if service_name in KubApiPodReader.get_pod_annotations(pod):
            service = KubApiPodReader.get_service_json(pod, service_name)
            return service.get('outputs', {})

        raise Exception(f"could not find service with name '{service_name}'")


class AwsServiceUpdater(IServiceUpdater):

    def __init__(self, status_maintainer: AWSStatusMaintainer, service_status_state: ServiceStatusState,
                 logger: Logger):
        super().__init__(service_status_state, logger)
        self._status_maintainer = status_maintainer

    @CallsLogger.wrap
    def on_update_status(self, name: str, status: str):
        with self.lock:
            self._status_maintainer.update_service_status(name=name, status=status)

    def update_deployment_outputs(self, service_name: str, outputs: {}):
        with self.lock:
            return self._status_maintainer.update_service_outputs(service_name, outputs)

    def get_deployment_outputs(self, service_name: str) -> {}:
        return self._status_maintainer.get_service_deployment_outputs(service_name)


class AzureServiceUpdater(IServiceUpdater):

    def update_deployment_outputs(self, service_name: str, outputs: {}):
        with self.lock:
            self._status_maintainer.update_service_outputs(name=service_name, outputs=outputs)

    def get_deployment_outputs(self, service_name: str) -> {}:
        return self._status_maintainer.get_service_deployment_outputs(service_name)

    def __init__(self, status_maintainer: AzureStatusMaintainer, service_status_state: ServiceStatusState,
                 logger: Logger):
        super().__init__(service_status_state, logger)
        self._status_maintainer = status_maintainer

    @CallsLogger.wrap
    def on_update_status(self, name: str, status: str):
        with self.lock:
            self._status_maintainer.update_service_status(name=name, status=status)
