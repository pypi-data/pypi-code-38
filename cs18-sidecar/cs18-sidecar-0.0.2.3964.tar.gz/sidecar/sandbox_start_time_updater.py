from abc import ABCMeta, abstractmethod
from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus
from sidecar.const import DateTimeProvider
from sidecar.health_check.app_health_check_state import AppHealthCheckState


class ISandboxStartTimeUpdater:
    __metaclass__ = ABCMeta

    def __init__(self,
                 app_health_check_state: AppHealthCheckState,
                 date_time_provider: DateTimeProvider,
                 logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):

        self._app_health_check_state = app_health_check_state
        self._date_time_provider = date_time_provider
        self._logger = logger
        self._apps_configuration_end_tracker = apps_configuration_end_tracker
        self._was_start_time_updated = False

    def on_app_instance_configuration_status_updated(self):
        # need this protection in order to set the start time only once
        # because this method can be called even after all apps already finished configuration
        # due to app instances being restarted and reconfigured
        if self._was_start_time_updated:
            return

        instances_complete_with_success = self._apps_configuration_end_tracker.all_apps_configuration_ended_with_status(
            AppConfigurationEndStatus.COMPLETED)

        apps_complete_with_success = self._app_health_check_state.all_complete_with_success()

        if instances_complete_with_success and apps_complete_with_success:
            curr_time = self._date_time_provider.get_current_time_utc()
            self._logger.info('health check done time: {}'.format(curr_time))
            self._on_health_check_done()
            self._was_start_time_updated = True

    @abstractmethod
    def _on_health_check_done(self):
        raise NotImplementedError
