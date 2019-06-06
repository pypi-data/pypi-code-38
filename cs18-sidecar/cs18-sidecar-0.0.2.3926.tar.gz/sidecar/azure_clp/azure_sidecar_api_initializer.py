from logging import Logger

from sidecar.configuration_start_policy import ConfigurationStartPolicy
from sidecar.app_instance_config_status_event_reporter import AppInstanceConfigStatusEventReporter
from sidecar.app_instance_service import IAppInstanceService
from sidecar.app_services.app_service import AzureAppService
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.azure_clp.azure_app_instance_identifier_creator import AzureAppInstanceIdentifierCreator
from sidecar.azure_clp.azure_app_instance_service import AzureAppInstanceService
from sidecar.azure_clp.azure_clients import AzureClientsManager, AzureCredentialsProvider
from sidecar.azure_clp.azure_sandbox_deployment_end_updater import AzureSandboxDeploymentEndUpdater
from sidecar.azure_clp.azure_sandbox_start_time_updater import AzureSandboxStartTimeUpdater
from sidecar.azure_clp.azure_status_maintainer import AzureStatusMaintainer
from sidecar.azure_clp.azure_table_service import AzureTableService
from sidecar.const import DateTimeProvider
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.model.objects import AzureSidecarConfiguration
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater
from sidecar.sandbox_deployment_state_tracker import SandboxDeploymentStateTracker
from sidecar.services.service_status_state import ServiceStatusState


class AzureSidecarApiInitializer:
    def __init__(self,
                 service_execution_end_tracker: ServiceStatusState,
                 config: AzureSidecarConfiguration,
                 app_instance_status_event_reporter: AppInstanceConfigStatusEventReporter,
                 app_health_check_state: AppHealthCheckState,
                 logger: Logger) -> None:
        super().__init__()
        self._service_execution_end_tracker = service_execution_end_tracker
        self._config = config
        self._app_health_check_state = app_health_check_state
        self._app_instance_status_event_reporter = app_instance_status_event_reporter
        self._logger = logger

    def initialize(self):
        app_instance_identifier_creator = AzureAppInstanceIdentifierCreator(logger=self._logger)
        azure_credentials_provider = self._create_credentials_provider()
        azure_clients_manager = AzureClientsManager(credentials_provider=azure_credentials_provider)

        data_store_service = AzureTableService(azure_clients_manager.table_service)
        data_store_service.create_table()

        azure_status_maintainer = AzureStatusMaintainer(data_store_service=data_store_service,
                                                        sandbox_id=self._config.sandbox_id)

        azure_app_instance_service = AzureAppInstanceService(logger=self._logger,
                                                             sandbox_id=self._config.sandbox_id,
                                                             clients_manager=azure_clients_manager,
                                                             status_maintainer=azure_status_maintainer)

        azure_sandbox_deployment_end_updater = AzureSandboxDeploymentEndUpdater(
            status_maintainer=azure_status_maintainer)

        apps_configuration_end_tracker = self._create_apps_configuration_end_tracker(
            app_instance_service=azure_app_instance_service)

        start_time_updater = AzureSandboxStartTimeUpdater(
            app_health_check_state=self._app_health_check_state,
            date_time_provider=DateTimeProvider(),
            logger=self._logger,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            status_maintainer=azure_status_maintainer)

        app_status_maintainer, \
        app_configuration_start_policy, \
        sandbox_deployment_state_tracker = self._create_cp_agnostic_components(
            app_instance_service=azure_app_instance_service,
            sandbox_deployment_end_updater=azure_sandbox_deployment_end_updater,
            apps_configuration_end_tracker=apps_configuration_end_tracker)

        app_service = AzureAppService(logger=self._logger)

        return app_status_maintainer, \
               app_configuration_start_policy, \
               app_instance_identifier_creator, \
               apps_configuration_end_tracker, \
               app_service, \
               sandbox_deployment_state_tracker, \
               start_time_updater, \
               azure_status_maintainer

    def _create_apps_configuration_end_tracker(self, app_instance_service: IAppInstanceService):
        return AppsConfigurationEndTracker(logger=self._logger,
                                           apps=self._config.apps,
                                           app_instance_service=app_instance_service)

    def _create_cp_agnostic_components(self, app_instance_service: IAppInstanceService,
                                       sandbox_deployment_end_updater: ISandboxDeploymentEndUpdater,
                                       apps_configuration_end_tracker: AppsConfigurationEndTracker):
        sandbox_deployment_state_tracker = SandboxDeploymentStateTracker(
            logger=self._logger,
            apps=self._config.apps,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            sandbox_deployment_end_updater=sandbox_deployment_end_updater,
            space_id=self._config.space_id)

        app_status_maintainer = AppStatusMaintainer(
            logger=self._logger,
            app_instance_service=app_instance_service,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            sandbox_deployment_state_tracker=sandbox_deployment_state_tracker,
            app_instance_status_event_reporter=self._app_instance_status_event_reporter)

        app_configuration_start_policy = ConfigurationStartPolicy(
            app_health_check_state=self._app_health_check_state,
            apps_config_end_tracker=apps_configuration_end_tracker,
            apps=self._config.apps,
            services=self._config.services,
            service_status_state=self._service_execution_end_tracker)

        return app_status_maintainer, app_configuration_start_policy, sandbox_deployment_state_tracker

    def _create_credentials_provider(self):
        return AzureCredentialsProvider(
            management_resource_group=self._config.management_resource_group,
            subscription_id=self._config.subscription_id,
            application_id=self._config.application_id,
            application_secret=self._config.application_secret,
            tenant_id=self._config.tenant_id)
