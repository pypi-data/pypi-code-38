import threading

from sidecar.apps_configuration_end_tracker import AppConfigurationEndStatus
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.messaging_service import MessagingService
from sidecar.model.objects import EnvironmentType
from sidecar.sandbox_deployment_state_tracker import SandboxDeploymentStateTracker


class SandboxEndDeploymentNotifier:
    def __init__(self,
                 deployment_state_tracker: SandboxDeploymentStateTracker,
                 messaging_service: MessagingService,
                 app_health_state_checker: AppHealthCheckState,
                 space_id: str,
                 sandbox_id: str,
                 production_id: str,
                 env_type: EnvironmentType):
        self._sandbox_id = sandbox_id
        self._production_id = production_id
        self._space_id = space_id
        self._app_health_state_checker = app_health_state_checker
        self._messaging_service = messaging_service
        self._deployment_state_tracker = deployment_state_tracker
        self._is_message_sent = False
        self._lock = threading.RLock()
        self._env_type = env_type

    # please never use git history on this, it's not my fault.
    def notify_end_deployment(self):

        with self._lock:
            if self._is_message_sent:
                return

            if self._deployment_state_tracker.all_apps_deployment_ended_with_status(AppConfigurationEndStatus.COMPLETED) \
                    and self._app_health_state_checker.all_complete_with_success():

                end_status = self._deployment_state_tracker.get_deployment_end_status()

                if self._env_type == EnvironmentType.Sandbox:
                    message_type = 'CSMSCommon.Model.Events:SandboxDeployed'
                    message_data = {
                        'SpaceId': self._space_id,
                        'SandboxId': self._sandbox_id,
                        'Status': end_status
                    }
                else:
                    message_type = 'CSMSCommon.Model.Events:ProductionDeployed'
                    message_data = {
                        'SpaceId': self._space_id,
                        'SandboxId': self._sandbox_id,
                        'ProductionId': self._production_id,
                        'Status': end_status,
                        'EnvironmentType': self._get_production_env_type()
                    }

                self._messaging_service.publish(message_type, message_data)
                self._is_message_sent = True

    def _get_production_env_type(self):
        if self._env_type == EnvironmentType.ProductionBlue:
            return 'blue'
        elif self._env_type == EnvironmentType.ProductionGreen:
            return 'green'
        else:
            raise ValueError("EnvironmentType value of '{}' is neither 'blue' nor 'green'".format(self._env_type))
