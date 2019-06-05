from sidecar.const import Const
from sidecar.kub_api_service import IKubApiService
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater


class KubSandboxDeploymentEndUpdater(ISandboxDeploymentEndUpdater):
    def __init__(self,
                 kub_api_service: IKubApiService):
        super(KubSandboxDeploymentEndUpdater, self).__init__()
        self.kub_api_service = kub_api_service

    def _set_deployment_end_details(self, deployment_end_status: str):
        annotations = {Const.SANDBOX_DEPLOYMENT_END_STATUS: deployment_end_status,
                       Const.SANDBOX_DEPLOYMENT_END_STATUS_v2: deployment_end_status}
        self.kub_api_service.update_namespace(annotations)
