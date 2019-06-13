from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.azure_clp.azure_status_maintainer import AzureStatusMaintainer
from sidecar.const import DateTimeProvider
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class AzureSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self, date_time_provider: DateTimeProvider, logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 status_maintainer: AzureStatusMaintainer,
                 app_health_check_state: AppHealthCheckState):
        super(AzureSandboxStartTimeUpdater, self).__init__(
            app_health_check_state=app_health_check_state,
            date_time_provider=date_time_provider,
            logger=logger,
            apps_configuration_end_tracker=apps_configuration_end_tracker)
        self._status_maintainer = status_maintainer

    def _on_health_check_done(self):
        # TODO: need to wait for completion? Of what?
        # _thread.start_new_thread(self._wait_for_stack_complete, ())
        self._update_sidecar_start_time()

    # def _wait_for_stack_complete(self):
    #     waiter = self._cfclient.get_waiter('stack_create_complete')
    #     stack_name = self._get_stack_name(self.sandbox_id)
    #
    #     self._logger.info('waiting for stack_create_complete state')
    #     waiter.wait(StackName=stack_name)
    #     self._logger.info('stack completed!')
    #     self._update_sidecar_start_time()

    def _update_sidecar_start_time(self):
        self._status_maintainer.update_sandbox_start_status(self._date_time_provider.get_current_time_utc())

    # @staticmethod
    # def _get_stack_name(sandbox_id: str):
    #     return 'sandbox-{0}'.format(sandbox_id)
