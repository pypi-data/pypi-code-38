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


class IServiceStatusUpdater(metaclass=ABCMeta):
    def __init__(self, service_status_state: ServiceStatusState, logger: Logger):
        self.service_status_state = service_status_state
        self.logger = logger
        self.lock = threading.RLock()

    @CallsLogger.wrap
    def update(self, name: str, status: str):
        self.update_impl(name=name, status=status)
        self.service_status_state.update_status(name=name, status=status)

    @abstractmethod
    def update_impl(self, name: str, status: str):
        raise NotImplemented()


class K8SServiceStatusUpdater(IServiceStatusUpdater):

    def __init__(self, kub_api_service: IKubApiService, service_status_state: ServiceStatusState, logger: Logger):
        super().__init__(service_status_state, logger)
        self._k8s_service = kub_api_service

    @CallsLogger.wrap
    def update_impl(self, name: str, status: str):
        with self.lock:
            pod = Utils.retry_on_exception(
                func=lambda: self._k8s_service.get_pod_by_name(name=Const.SERVICE_EXECUTION_POD),
                logger=self.logger,
                logger_msg="trying to get service execution pod")

            if pod and not KubApiPodReader.is_pod_ended(pod) and not KubApiPodReader.is_pod_terminating(pod):
                service_data = json.loads(pod['metadata']['annotations'][name])
                service_data["status"] = status
                annotation_change = {name: json.dumps(service_data)}
                self._k8s_service.update_pod(Const.SERVICE_EXECUTION_POD, annotation_change)


class AwsServiceStatusUpdater(IServiceStatusUpdater):

    def __init__(self, status_maintainer: AWSStatusMaintainer, service_status_state: ServiceStatusState,
                 logger: Logger):
        super().__init__(service_status_state, logger)
        self._status_maintainer = status_maintainer

    @CallsLogger.wrap
    def update_impl(self, name: str, status: str):
        with self.lock:
            self._status_maintainer.update_service_status(name=name, status=status)


class AzureServiceStatusUpdater(IServiceStatusUpdater):

    def __init__(self, status_maintainer: AzureStatusMaintainer, service_status_state: ServiceStatusState,
                 logger: Logger):
        super().__init__(service_status_state, logger)
        self._status_maintainer = status_maintainer

    @CallsLogger.wrap
    def update_impl(self, name: str, status: str):
        with self.lock:
            self._status_maintainer.update_service_status(name=name, status=status)
