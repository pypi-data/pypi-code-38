from sidecar.app_instance_event_handler import AppInstanceEventHandler
from sidecar.app_instance_events import AppInstanceEvents
from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.const import AppInstanceConfigStatus
from logging import Logger


class AppInstanceConfigStatusEventReporter:
    def __init__(self, app_instance_event_handler: AppInstanceEventHandler, logger: Logger) -> None:
        super().__init__()
        self.logger = logger
        self._app_instance_event_handler = app_instance_event_handler

    def on_app_instance_configuration_status_updated(self, app_instance_identifier: AppInstanceIdentifier,
                                                     app_instance_config_status: str):
        app_instance_event = self._convert_to_app_instance_event(app_instance_config_status, logger=self.logger)
        self._app_instance_event_handler.report_event(app_instance_identifier, app_instance_event)

    @staticmethod
    def _convert_to_app_instance_event(app_instance_config_status: str, logger: Logger) -> str:
        if app_instance_config_status == AppInstanceConfigStatus.PENDING:
            return AppInstanceEvents.RunningHealthCheck
        if app_instance_config_status == AppInstanceConfigStatus.COMPLETED:
            return AppInstanceEvents.DeploymentCompleted
        if app_instance_config_status == AppInstanceConfigStatus.ERROR:
            return AppInstanceEvents.DeploymentFailed
        raise Exception("unknown AppInstanceConfigStatus '{status}'".format(status=app_instance_config_status))
