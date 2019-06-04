from logging import Logger

from datetime import datetime
from typing import Tuple

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.cloud_logger.file_logger import ICloudLogger
from sidecar.cloud_logger.logs import AppLogEntry
from sidecar.const import DateTimeProvider


class AppInstanceEventHandler:
    CloudLoggerEventsTopic = "events"

    def __init__(self, cloud_logger: ICloudLogger, date_time_provider: DateTimeProvider, logger: Logger) -> None:
        super().__init__()
        self.logger = logger
        self._cloud_logger = cloud_logger
        self._date_time_provider = date_time_provider

    def report_event(self, app_instance_identifier: AppInstanceIdentifier, app_instance_event: str):
        self._write_event_to_cloud_log(app_instance_identifier, app_instance_event)

    def _write_event_to_cloud_log(self, app_instance_identifier: AppInstanceIdentifier, app_instance_event: str):
        app_instance_log_event = self._create_app_instance_log_event(app_instance_event)
        log_entry = AppLogEntry(app=app_instance_identifier.name, instance=app_instance_identifier.infra_id,
                                topic=self.CloudLoggerEventsTopic, log_events=[app_instance_log_event], log_type="Events")
        self.logger.info(log_entry.get_as_string())
        self._cloud_logger.write(log_entry=log_entry)

    def _create_app_instance_log_event(self, app_instance_event) -> Tuple[datetime, str]:
        event_time = self._date_time_provider.get_current_time_utc()
        return event_time, app_instance_event
