from sidecar.azure_clp.azure_status_maintainer import AzureStatusMaintainer
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater


class AzureSandboxDeploymentEndUpdater(ISandboxDeploymentEndUpdater):
    def __init__(self, status_maintainer: AzureStatusMaintainer):
        super(AzureSandboxDeploymentEndUpdater, self).__init__()
        self._status_maintainer = status_maintainer

    def _set_deployment_end_details(self, deployment_end_status: str):
        self._status_maintainer.update_sandbox_end_status(deployment_end_status)
