import threading
from logging import Logger

from sidecar.app_instance_identifier import AppInstanceIdentifier, IIdentifier
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.cloud_logger.file_logger import ICloudLogger
from sidecar.const import AppInstanceConfigStatus
from sidecar.health_check.health_check_executor import HealthCheckExecutor
from sidecar.health_check.health_check_preparer import HealthCheckPreparer
from sidecar.utils import CallsLogger

HEALTH_CHECK_TOPIC = "healthcheck"


class AppInstanceHealthCheckMonitor:
    def __init__(self,
                 executor: HealthCheckExecutor,
                 preparer: HealthCheckPreparer,
                 status_maintainer: AppStatusMaintainer,
                 cloud_logger: ICloudLogger,
                 logger: Logger):
        self._status_maintainer = status_maintainer
        self._cloud_logger = cloud_logger
        self._preparer = preparer
        self._executor = executor
        self._logger = logger

    @CallsLogger.wrap
    def start(self, address: str, identifier: IIdentifier):
        thread = threading.Thread(target=self.process_health_check, args=(address, identifier))
        thread.start()

    def process_health_check(self, ip_address: str, identifier: AppInstanceIdentifier):
        try:
            status = AppInstanceConfigStatus.PENDING
            self._status_maintainer.update_status(app_instance_identifier=identifier,
                                                  status=status)

            result = self._execute_health_check_script(identifier=identifier,
                                                       ip_address=ip_address)

            status = AppInstanceConfigStatus.COMPLETED if result else AppInstanceConfigStatus.ERROR
            self._status_maintainer.update_status(app_instance_identifier=identifier,
                                                  status=status)
        except Exception as ex:
            self._logger.exception("error - identifier: '{}', ip: '{}'. {}".format(
                identifier,
                ip_address,
                str(ex)))
            raise

    def _execute_health_check_script(self,
                                     identifier,
                                     ip_address: str) -> bool:
        cmd = self._preparer.prepare(app_name=identifier.name,
                                     address=ip_address)

        return self._executor.start(identifier=identifier,
                                    cmd=cmd)
