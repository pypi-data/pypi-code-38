"""
Helm subcommand
"""
from compose_flow.kube.mixins import KubeMixIn
from .passthrough_base import PassthroughBaseSubcommand


class Kubectl(PassthroughBaseSubcommand, KubeMixIn):
    """
    Subcommand for running rancher CLI commands
    """

    command_name = 'kubectl'

    setup_environment = True

    setup_profile = False

    def handle(self, extra_args: list = None) -> [None, str]:
        self.switch_kube_context()

        return super().handle(log_output=False)
