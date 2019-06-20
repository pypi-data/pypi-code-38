import json
import threading
from logging import Logger
from typing import Dict, List

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_service import IAppInstanceService
from sidecar.const import AppInstanceConfigStatus
from sidecar.model.objects import SidecarApplication


class AppConfigurationEndStatus:
    NONE = "none"
    COMPLETED = "completed"
    ERROR = "error"

    def __init__(self, status: str, is_config_ended: bool):
        self.status = status
        self.is_config_ended = is_config_ended

    def is_ended_with_status(self, required_status: str) -> bool:
        return self.is_config_ended and self.status == required_status

    def __repr__(self):
        return self.status


class AppRecord:
    def __init__(self, app_name: str, expected_instances_count: int):
        self.app_name = app_name
        self.expected_instances_count = expected_instances_count
        self.instance_config_end_statuses = {}

    def update_instance_config_end_status(self, config_end_status: str, app_instance_identifier: AppInstanceIdentifier):
        # if an end status was already reported from the same infra_id - it will be overridden
        # this is in order to support app container restart on the same pod
        self.instance_config_end_statuses[app_instance_identifier.infra_id] = config_end_status

    def clear_instance_config_end_status(self, app_instance_identifier: AppInstanceIdentifier) -> bool:
        exists = app_instance_identifier.infra_id in self.instance_config_end_statuses
        if exists:
            self.remove_app_instance_identifier(app_instance_identifier=app_instance_identifier)
        return exists

    def clear_all_end_statuses(self):
        self.instance_config_end_statuses.clear()

    def app_configuration_ended(self) -> bool:
        return self.expected_instances_count - len(self.instance_config_end_statuses) == 0

    def get_current_config_end_status(self) -> AppConfigurationEndStatus:
        is_config_ended = self.app_configuration_ended()

        current_config_end_statuses = list(self.instance_config_end_statuses.values())
        if not current_config_end_statuses:
            return AppConfigurationEndStatus(AppConfigurationEndStatus.NONE, is_config_ended)

        if any(status == AppInstanceConfigStatus.ERROR for status in current_config_end_statuses):
            return AppConfigurationEndStatus(AppConfigurationEndStatus.ERROR, is_config_ended)

        if all(status == AppInstanceConfigStatus.COMPLETED for status in current_config_end_statuses):
            return AppConfigurationEndStatus(AppConfigurationEndStatus.COMPLETED, is_config_ended)

        raise Exception("could not calculate app configuration end status from: {}".format(",".join(current_config_end_statuses)))

    def get_ended_app_instance_identifiers(self) -> List[AppInstanceIdentifier]:
        return [AppInstanceIdentifier(self.app_name, infra_id) for infra_id in self.instance_config_end_statuses]

    def remove_app_instance_identifier(self, app_instance_identifier: AppInstanceIdentifier):
        del self.instance_config_end_statuses[app_instance_identifier.infra_id]


class IAppInstanceRetriever(object):
    pass


class AppsConfigurationEndTracker:
    def __init__(self, logger: Logger,
                 apps: List[SidecarApplication],
                 app_instance_service: IAppInstanceService):
        self._app_instance_service = app_instance_service
        self._logger = logger
        self._apps = apps
        self._lock = threading.RLock()
        self._app_records = self._build_app_records(apps)

    def update_app_instance_config_status(self, app_instance_identifier: AppInstanceIdentifier,
                                          app_instance_config_status: str):
        with self._lock:
            self._invalidate_app_records()
            self._update_app_config_status(app_instance_identifier, app_instance_config_status)
            self._log_current_state()

    def all_apps_configuration_ended(self) -> bool:
        with self._lock:
            return all(record.app_configuration_ended() for record in self._app_records.values())

    def all_apps_configuration_ended_with_status(self, required_status: str) -> bool:
        with self._lock:
            return all(record.get_current_config_end_status().is_ended_with_status(required_status)
                       for record in self._app_records.values())

    def get_all_app_configuration_statuses(self) -> Dict[str, AppConfigurationEndStatus]:
        with self._lock:
            return {app_name: app_record.get_current_config_end_status()
                    for app_name, app_record in self._app_records.items()}

    def get_app_configuration_statuses(self, *app_names: str) -> Dict[str, AppConfigurationEndStatus]:
        with self._lock:
            app_statuses = {app_name: self._app_records[app_name].get_current_config_end_status()
                            for app_name in app_names}
            return app_statuses

    @staticmethod
    def _build_app_records(app_requests: List[SidecarApplication]) -> Dict[str, AppRecord]:
        app_records = {app_request.name: AppRecord(app_name=app_request.name,
                                                   expected_instances_count=app_request.instances_count)
                       for app_request in app_requests}
        return app_records

    def _invalidate_app_records(self):
        # we could have implemented the syncing of the cache by just re-caching all the app instances' end statuses
        # from the cloud provider, but instead we're removing the no longer existing instances and their statuses.
        # this is because sometimes there is a small delay from when the status is set until it is returned on
        # querying the cloud provider, so we might miss some statuses due to timing issues.
        missing_identifiers = self._get_missing_app_instance_identifiers()
        if missing_identifiers:
            for missing_identifier in missing_identifiers:
                self._app_records[missing_identifier.name].remove_app_instance_identifier(missing_identifier)

            self._logger.warning("{count} of the configured app instances were purged from the cache: {details}"
                                 .format(count=len(missing_identifiers),
                                         details='; '.join(str(app_id) for app_id in missing_identifiers)))

    def _get_missing_app_instance_identifiers(self) -> List[AppInstanceIdentifier]:
        cached_app_instance_identifiers = set(app_instance_id
                                              for app_record in self._app_records.values()
                                              for app_instance_id in app_record.get_ended_app_instance_identifiers())
        if not cached_app_instance_identifiers:
            return []

        actual_app_instance_identifiers = set(self._app_instance_service.
                                              check_which_exist(identifiers=list(cached_app_instance_identifiers)))
        missing_identifiers = list(cached_app_instance_identifiers - actual_app_instance_identifiers)
        return missing_identifiers

    def _log_current_state(self):
        self._logger.info("the current state of app records:\n{APP_RECORDS}"
                          .format(APP_RECORDS=json.dumps(self._app_records, default=lambda x: x.__dict__, indent=2)))

    def _update_app_config_status(self, app_instance_identifier: AppInstanceIdentifier,
                                  app_instance_config_status: str):
        app_record = self._app_records[app_instance_identifier.name]
        if AppInstanceConfigStatus.is_end_status(app_instance_config_status):
            app_record.update_instance_config_end_status(app_instance_config_status, app_instance_identifier)
        else:
            app_record.clear_instance_config_end_status(app_instance_identifier=app_instance_identifier)
