from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater
from sidecar.aws_status_maintainer import AWSStatusMaintainer


class AwsSandboxDeploymentEndUpdater(ISandboxDeploymentEndUpdater):
    def __init__(self, aws_status_maintainer: AWSStatusMaintainer):
        super(AwsSandboxDeploymentEndUpdater, self).__init__()
        self._aws_status_maintainer = aws_status_maintainer

    def _set_deployment_end_details(self, deployment_end_status: str):
        self._aws_status_maintainer.update_sandbox_end_status(deployment_end_status)
