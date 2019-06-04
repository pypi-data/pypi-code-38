import datetime
import os
from os.path import expanduser


class ServiceType:
    TerraForm = "TerraForm"


class SidecarFilesStructure:
    FTP_FOLDER = "/var/ftp"

    @staticmethod
    def get_ftp_folder(app_name: str):
        return os.path.join(SidecarFilesStructure.FTP_FOLDER, app_name)

    # @staticmethod
    # def get_service_folder(name: str):
    #     return os.path.join(SidecarFilesStructure().get_ftp_folder(name))


# class ServiceKind:
#     TerraForm = "TerraForm"


class Signals:
    ON_INSTANCE_UPDATE_STATUS = "ON_INSTANCE_UPDATE_STATUS"
    ON_APPS_DEPLOYMENT_COMPLETE = "ON_APPS_DEPLOYMENT_COMPLETE"


class AppNetworkStatus:
    PENDING = "pending"
    TESTING_PUBLIC_NETWORK = "testing_public_network"
    TESTING_PRIVATE_NETWORK = "testing_private_network"
    COMPLETED = "completed"
    ERROR = "error"

    @staticmethod
    def is_end_status(status: str) -> bool:
        return status in [AppNetworkStatus.COMPLETED, AppNetworkStatus.ERROR]

    @staticmethod
    def passed_internal_network_test(status: str) -> bool:
        return status in [AppNetworkStatus.TESTING_PUBLIC_NETWORK, AppNetworkStatus.COMPLETED]


class DateTimeProvider:
    def get_current_time_utc(self):
        return datetime.datetime.now(datetime.timezone.utc)


class AppInstanceConfigStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"

    END_STATUSES = [COMPLETED, ERROR]

    @staticmethod
    def is_end_status(status: str) -> bool:
        return status in AppInstanceConfigStatus.END_STATUSES


class SandboxDeploymentEndStatus:
    COMPLETED = "completed"
    ERROR = "error"


def _get_tag_name(tag_name: str):
    return 'colony-{}'.format(tag_name)


def get_app_selector(app_name: str):
    return _get_tag_name('selector-{app_name}'.format(app_name=app_name))


class Const:
    EXTERNAL_ELB_DNS_NAME = _get_tag_name('external-elb-dsn')
    APP_STATE_KEY_VALUE_SEPARATOR = ":"
    APP_NAME_TAG = _get_tag_name('app-name')
    APP_STATUS_TAG = _get_tag_name('app-status')
    APPS = _get_tag_name('apps')
    HEALTH_CHECK_STATUS = _get_tag_name("health-check-status")
    PRODUCTION_ID_TAG = _get_tag_name('production-id')
    SANDBOX_ID_TAG = _get_tag_name('sandbox-id')
    SANDBOX_START_TIME = 'start-time'
    SANDBOX_START_TIME_v2 = _get_tag_name('start-time')

    SANDBOX_DEPLOYMENT_END_STATUS = 'deployment-end-status'
    SANDBOX_DEPLOYMENT_END_STATUS_v2 = _get_tag_name('deployment-end-status')
    CSV_TAG_VALUE_SEPARATE = ","

    K8S_SIDECAR_SERVICE = 'sidecar-service'
    K8S_SIDECAR_APP_SELECTOR = get_app_selector(K8S_SIDECAR_SERVICE)

    AWS_SIDECAR_APP_NAME = 'colonySidecar'

    QUALY_SERVICE_NAME = 'colonyDebugService'

    SIDECAR_HOME_FOLDER = os.path.join(expanduser("~"), 'sidecar')

    INSTANCELOGICALID = _get_tag_name('instance-logical-id')
    EXTERNAL_PORTS = _get_tag_name('external-ports')
    INTERNAL_PORTS = _get_tag_name('internal-ports')
    MAIN_ALB = "MainALB"
    MAIN_ALB_SG = 'MainALBSG'

    SERVICE_EXECUTION_POD = _get_tag_name('service-execution-pod')

    @staticmethod
    def get_config_file():
        return '{HOME_FOLDER}/config.json'.format(HOME_FOLDER=Const.SIDECAR_HOME_FOLDER)

    @staticmethod
    def get_log_file():
        return '{HOME_FOLDER}/log.txt'.format(HOME_FOLDER=Const.SIDECAR_HOME_FOLDER)

    @staticmethod
    def get_kubernetes_token_file_path() -> str:
        return '/var/run/secrets/kubernetes.io/serviceaccount/token'

    @staticmethod
    def get_app_folder(app_name: str) -> str:
        return '{HOME_FOLDER}/{APP_NAME}'.format(HOME_FOLDER=Const.SIDECAR_HOME_FOLDER,
                                                 APP_NAME=app_name)

    @staticmethod
    def get_app_log_file(app_name: str) -> str:
        return '{APP_FOLDER}/log.txt'.format(APP_FOLDER=Const.get_app_folder(app_name=app_name),
                                             app_name=app_name)

    @staticmethod
    def get_health_check_file(app_name: str, script_name: str) -> str:
        return '{APP_FOLDER}/{SCRIPT_NAME}'.format(
            APP_FOLDER=Const.get_app_folder(app_name=app_name), SCRIPT_NAME=script_name)
