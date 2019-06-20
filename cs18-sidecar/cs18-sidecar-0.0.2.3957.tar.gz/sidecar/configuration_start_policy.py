from typing import List, Tuple

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus
from sidecar.const import AppNetworkStatus
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.model.objects import SidecarApplication, ISidecarService
from sidecar.sandbox_terminating_query import ISandboxTerminatingQuery
from sidecar.services.service_status_state import ServiceStatusState


class ConfigurationStartStatus:
    START = "start"
    WAIT = "wait"
    CANCEL = "cancel"


class ConfigurationStartPolicy:
    def __init__(self,
                 service_status_state: ServiceStatusState,
                 app_health_check_state: AppHealthCheckState,
                 apps_config_end_tracker: AppsConfigurationEndTracker,
                 apps: List[SidecarApplication],
                 services: List[ISidecarService],
                 terminating_query: ISandboxTerminatingQuery = None):
        self._service_status_state = service_status_state
        self._services = services
        self._apps = apps
        self._app_health_check_state = app_health_check_state
        self._apps_config_end_tracker = apps_config_end_tracker

        self._app_dependencies = {app.name: list(app.dependencies) for app in apps}
        self._service_dependencies = {service.name: list([d for d in service.dependencies]) for service in services}

        self._dependencies = {**self._app_dependencies, **self._service_dependencies}

        self._terminating_query = terminating_query

    def get_configuration_start_status(self, name: str) -> str:
        if self._terminating_query and self._terminating_query.is_terminating():
            return ConfigurationStartStatus.CANCEL

        dependencies = self._dependencies[name]
        if not dependencies:
            return ConfigurationStartStatus.START

        app_dependencies, service_dependencies = self.split_dependencies_by_type(dependencies)

        app_dependency_statuses = self._apps_config_end_tracker.get_app_configuration_statuses(*app_dependencies)
        all_instances_completed_with_success = all(
            config_end_status.is_ended_with_status(AppConfigurationEndStatus.COMPLETED) for config_end_status in
            app_dependency_statuses.values())

        all_apps_completed_private_network_health_check = all(
            AppNetworkStatus.passed_internal_network_test(status)
            for status
            in self._app_health_check_state.get_apps_state(app_dependencies).values())

        all_service_dependencies_ended_with_success = \
            self._service_status_state.execution_done(names=service_dependencies)

        if all_instances_completed_with_success and \
                all_apps_completed_private_network_health_check and \
                all_service_dependencies_ended_with_success:
            return ConfigurationStartStatus.START

        return ConfigurationStartStatus.WAIT

    def split_dependencies_by_type(self, dependencies: List[str]) -> Tuple[List[str], List[str]]:
        apps = []
        services = []
        for d in dependencies:
            if d in self._app_dependencies:
                apps.append(d)
            if d in self._service_dependencies:
                services.append(d)
        return apps, services
