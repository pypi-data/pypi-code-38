from abc import ABCMeta, abstractmethod


class ISandboxDeploymentEndUpdater:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def on_sandbox_deployment_ended(self, deployment_end_status: str):
        self._set_deployment_end_details(deployment_end_status=deployment_end_status)

    @abstractmethod
    def _set_deployment_end_details(self, deployment_end_status: str):
        raise NotImplementedError
