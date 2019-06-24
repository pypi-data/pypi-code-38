import json
import threading
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus
from sidecar.const import AppInstanceConfigStatus, SandboxDeploymentEndStatus
from sidecar.model.objects import SidecarApplication
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater


class SandboxDeploymentStateTracker:
    def __init__(self, logger: Logger,
                 apps: List[SidecarApplication],
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 sandbox_deployment_end_updater: ISandboxDeploymentEndUpdater,
                 space_id: str):
        self._logger = logger
        self._apps_configuration_end_tracker = apps_configuration_end_tracker
        self._sandbox_deployment_end_updater = sandbox_deployment_end_updater
        self._app_deployment_end_statuses = {app.name: None for app in apps}
        self._remaining_app_config_counts = {app.name: app.instances_count * 2 for app in apps}
        self._deployment_end_status = None
        self.space_id = space_id

        self._lock = threading.RLock()

    def on_app_instance_configuration_status_updated(self, app_instance_identifier: AppInstanceIdentifier,
                                                     app_instance_config_status: str):
        with self._lock:
            if self._is_deployment_ended():
                return
            self._handle_if_configuration_starting(app_instance_identifier.name, app_instance_config_status)
            self._update_app_deployment_end_statuses()
            self._set_is_deployment_ended()

    def all_apps_deployment_ended_with_status(self, required_app_status: str) -> bool:
        with self._lock:
            return all(self._is_app_deployment_ended_with_status(end_status, required_app_status)
                       for end_status in self._app_deployment_end_statuses.values())

    def get_deployment_end_status(self) -> str:
        with self._lock:
            return self._deployment_end_status

    def _update_app_deployment_end_statuses(self):
        # checking which of the non-deployed apps have finished configuration, i.e. became deployed.
        # doing it for all apps and not only the one whose status was updated because don't want to assume
        # which changes have occurred in the cloud provider and analyzing its state as a whole
        non_deployed_app_names = [name
                                  for name, status in self._app_deployment_end_statuses.items()
                                  if status is None]
        if not non_deployed_app_names:
            return

        app_deployed = False
        current_app_config_statuses = self. \
            _apps_configuration_end_tracker.get_app_configuration_statuses(*non_deployed_app_names)
        for app_name, config_end_status in current_app_config_statuses.items():
            # app deployment is considered to be ended only when all of its instances finished configuration
            if config_end_status.is_config_ended:
                self._app_deployment_end_statuses[app_name] = config_end_status.status
                app_deployed = True

        if app_deployed:
            self._logger.info("app deployment end statuses:\n{DEP_STATUSES}"
                              .format(DEP_STATUSES=json.dumps(self._app_deployment_end_statuses, indent=2)))

    def _handle_if_configuration_starting(self, app_name, app_instance_config_status):
        if app_instance_config_status == AppInstanceConfigStatus.PENDING:
            if self._remaining_app_config_counts[app_name] == 0:
                self._app_deployment_end_statuses[app_name] = AppConfigurationEndStatus.ERROR
                self._logger.info("the '{APP_NAME}' app has exceeded the allowed limit of configuring instances, "
                                  "setting the app's deployment status to '{DEP_STATUS}'."
                                  .format(APP_NAME=app_name,
                                          DEP_STATUS=self._app_deployment_end_statuses[app_name]))
            else:
                self._remaining_app_config_counts[app_name] -= 1

    def _set_is_deployment_ended(self):
        self._deployment_end_status = self._calc_deployment_end_status()

        if self._is_deployment_ended():
            end_status = self._deployment_end_status
            self._logger.info("sandbox deployment ended with status '{END_STATUS}'"
                              .format(END_STATUS=end_status))
            self._sandbox_deployment_end_updater.on_sandbox_deployment_ended(deployment_end_status=end_status)

    @staticmethod
    def _is_app_deployment_ended_with_status(actual_end_status: str, required_app_status: str) -> bool:
        return actual_end_status is not None and actual_end_status == required_app_status

    def _is_deployment_ended(self):
        return self._deployment_end_status is not None

    def _calc_deployment_end_status(self) -> str:
        # the deployment end status is set to error both in case of HC limit and in case of error being the HC result
        if any(status == AppConfigurationEndStatus.ERROR for status in self._app_deployment_end_statuses.values()):
            return SandboxDeploymentEndStatus.ERROR
        if all(status == AppConfigurationEndStatus.COMPLETED for status in self._app_deployment_end_statuses.values()):
            return SandboxDeploymentEndStatus.COMPLETED
        return None
