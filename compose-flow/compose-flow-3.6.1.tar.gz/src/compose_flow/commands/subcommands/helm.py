"""
Helm subcommand
"""
from compose_flow.kube.mixins import KubeMixIn
from .passthrough_base import PassthroughBaseSubcommand


class Helm(PassthroughBaseSubcommand, KubeMixIn):
    """
    Subcommand for running rancher CLI commands
    """

    command_name = 'helm'

    setup_environment = True

    setup_profile = False

    def handle(self, extra_args: list = None) -> [None, str]:
        self.switch_kube_context()

        return super().handle(log_output=True)
