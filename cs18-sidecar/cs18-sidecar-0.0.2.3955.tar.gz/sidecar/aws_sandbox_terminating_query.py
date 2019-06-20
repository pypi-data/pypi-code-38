from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.sandbox_terminating_query import ISandboxTerminatingQuery


class AwsSandboxTerminatingQuery(ISandboxTerminatingQuery):

    def __init__(self, status_maintainer: AWSStatusMaintainer):
        super().__init__()
        self._status_maintainer = status_maintainer

    def is_terminating(self) -> bool:
        return self._status_maintainer.get_terminating_flag()
