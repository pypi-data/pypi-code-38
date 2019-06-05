import threading
from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_session import AwsSession
from sidecar.const import DateTimeProvider
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater
from sidecar.aws_status_maintainer import AWSStatusMaintainer

from retrying import retry
from datetime import timedelta


class AwsSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self, app_health_check_state: AppHealthCheckState,
                 sandbox_id: str, aws_session: AwsSession,
                 date_time_provider: DateTimeProvider,
                 logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 aws_status_maintainer: AWSStatusMaintainer):
        super(AwsSandboxStartTimeUpdater, self).__init__(app_health_check_state, date_time_provider, logger,
                                                         apps_configuration_end_tracker)
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id
        self._date_time_provider = date_time_provider
        self._logger = logger
        self._cf_client = self.aws_session.get_cf_client()
        self.aws_status_maintainer = aws_status_maintainer

        # instead of a decorator so we can pass the logger to the _retry_if_throttling_error
        self._wait_for = retry(self._wait_for,
                               stop_max_attempt_number=5,
                               wait_fixed=15 * 1000,
                               retry_on_exception=self._retry_if_throttling_error)

    def _retry_if_throttling_error(self, e: Exception) -> bool:
        self._logger.error(f'Throttling on waiter: {e}')
        return 'Rate exceeded' in str(e)

    def _on_health_check_done(self):
        threading.Thread(target=self._wait_for_stack_complete, args=()).start()

    def _wait_for_stack_complete(self):
        stack_name = self.aws_session.sandbox_stack_name
        self._logger.info(f'waiting for stack "{stack_name}" to reach stack_create_complete state')
        self._wait_for('stack_create_complete', stack_name, delay=timedelta(seconds=10), timeout=timedelta(minutes=20))
        self._logger.info('stack completed!')
        self._update_sidecar_start_time()

    def _update_sidecar_start_time(self):
        self.aws_status_maintainer.update_sandbox_start_status(self._date_time_provider.get_current_time_utc())

    def _wait_for(self, waiter_name: str, stack_name: str, delay: timedelta, timeout: timedelta):
        max_attempts = int(timeout / delay)
        self._cf_client \
            .get_waiter(waiter_name) \
            .wait(StackName=stack_name, WaiterConfig={"Delay": delay.total_seconds(), "MaxAttempts": max_attempts})
