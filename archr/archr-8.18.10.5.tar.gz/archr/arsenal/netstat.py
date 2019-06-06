import contextlib
import logging
import os

from . import Bow

l = logging.getLogger("archr.arsenal.netstat")

class NetStatBow(Bow):
    """
    Runs a netstat inside the target.
    """

    REQUIRED_BINARY = "/bin/netstat"

    def fire(self, netstat_args="-tulnp"): #pylint:disable=arguments-differ
        """
        :param netstat_args: the arguments to netstat. default: "-tulnp"
        :return: Target instance returned by run_command
        """
        lines = self.target.run_command(args=["/tmp/netstat/fire", netstat_args]).stdout.read().splitlines()
