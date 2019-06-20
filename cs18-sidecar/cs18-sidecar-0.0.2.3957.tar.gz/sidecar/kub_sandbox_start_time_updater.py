from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.const import DateTimeProvider, Const
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.kub_api_service import IKubApiService
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class KubSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self,
                 app_health_check_state: AppHealthCheckState,
                 date_time_provider: DateTimeProvider,
                 logger: Logger,
                 kub_api_service: IKubApiService,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):
        super(KubSandboxStartTimeUpdater, self).__init__(app_health_check_state,
                                                         date_time_provider,
                                                         logger,
                                                         apps_configuration_end_tracker)
        self.kub_api_service = kub_api_service
        self.date_time_provider = date_time_provider

    def _on_health_check_done(self):
        time = str(self.date_time_provider.get_current_time_utc())
        annotations = {Const.SANDBOX_START_TIME: time, Const.SANDBOX_START_TIME_v2: time}
        self.kub_api_service.update_namespace(annotations)
