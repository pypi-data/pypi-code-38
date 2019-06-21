"""
Rancher CLI subcommand
"""
from compose_flow.kube.mixins import KubeMixIn
from .passthrough_base import PassthroughBaseSubcommand


class Rancher(PassthroughBaseSubcommand, KubeMixIn):
    """
    Subcommand for running rancher CLI commands
    """

    command_name = 'rancher'

    setup_environment = True

    setup_profile = False

    def handle(self, extra_args: list = None) -> [None, str]:
        self.switch_rancher_context()

        return super().handle(log_output=False)
