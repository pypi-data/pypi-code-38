import threading
from logging import Logger

from blinker import signal

from sidecar.app_instance_config_status_event_reporter import AppInstanceConfigStatusEventReporter
from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_service import IAppInstanceService
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.const import Signals
from sidecar.sandbox_deployment_state_tracker import SandboxDeploymentStateTracker


class AppStatusMaintainer:
    def __init__(self, logger: Logger,
                 app_instance_service: IAppInstanceService,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 sandbox_deployment_state_tracker: SandboxDeploymentStateTracker,
                 app_instance_status_event_reporter: AppInstanceConfigStatusEventReporter):
        self._logger = logger
        self._app_instance_service = app_instance_service
        self._apps_configuration_end_tracker = apps_configuration_end_tracker
        self._sandbox_deployment_state_tracker = sandbox_deployment_state_tracker
        self._app_instance_config_status_event_reporter = app_instance_status_event_reporter
        self._lock = threading.RLock()

    def update_status(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        # we want to report the event even if the instance is stale, so doing it before update_status_if_not_stale
        # the event handling should be able to handle concurrency so calling it outside the lock
        self._safely_report_app_instance_event(app_instance_identifier, status)

        with self._lock:
            # there are some scenarios where we might attempt to set a "stale" status that will override the most
            # recent one for the app instance.
            # for example, when there is a race condition involving health-checks:
            # 1. health check started -> app instance is restarted -> new instance starts another health check ->
            #    both health checks try to update their result status, in some order
            # 2. health check started -> app instance is restarted -> new instance will report end status via api and
            #    health check will try to update its result status, in some order
            #    [this scenario is no longer relevant since the api method that allows to set end status was removed]

            # _app_instance_service.update_status_if_not_stale is expected to prevent the wrong status from being
            # updated and throw an exception in this case so the flow doesn't continue.
            # it should implement the logic that if the updating app instance (identified by app_instance_identifier)
            # is no longer a part of the sandbox, then the update should not be performed (since the result is for
            # the instance before the restart). IMPORTANT: the identifier should be such that it changes on restart.
            # the validation could've been implemented out here, but it is better performance-wise to do it inside
            # _app_instance_service.update_status_if_not_stale (the instance is being fetched anyway).

            # currently, we assume that it is not possible that the same app instance (i.e. no restart, same id)
            # will try to set an end status more than once and so if the updating app instance is not stale we just
            # set the status without checking if this instance has already set an end status and whether it should
            # be overridden.
            # we might need to handle such scenarios in the future, for example if an app instance starts a health check
            # and then reports some end status via the api -> when the health check will end, it will try to override
            # the api's status with its own result.
            self._logger.info("updating app status '{APP_ID}' to '{STATUS}'"
                              .format(APP_ID=app_instance_identifier, STATUS=status))

            self._app_instance_service.update_status_if_not_stale(app_instance_identifier, status=status)

            self._apps_configuration_end_tracker.update_app_instance_config_status(
                app_instance_identifier=app_instance_identifier,
                app_instance_config_status=status)

            self._sandbox_deployment_state_tracker.on_app_instance_configuration_status_updated(
                app_instance_identifier=app_instance_identifier,
                app_instance_config_status=status)

        signal(Signals.ON_INSTANCE_UPDATE_STATUS)\
            .send(self, identifier=app_instance_identifier)

    def _safely_report_app_instance_event(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        # don't want unhandled errors in event handling to ruin the rest of the flow
        try:
            self._app_instance_config_status_event_reporter.on_app_instance_configuration_status_updated(
                app_instance_identifier=app_instance_identifier,
                app_instance_config_status=status)
        except Exception as exc:
            self._logger.exception("Failed to _safely_report_app_instance_event for app '{0}' exception {1}".format(app_instance_identifier.name, str(exc)))
