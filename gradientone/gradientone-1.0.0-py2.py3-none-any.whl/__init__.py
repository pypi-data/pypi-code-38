import gateway_helpers
import gateway_client
import controllers
import transmitters
import always_on
from version import __version__


__all__ = ['base', 'base_drivers', 'command_runners', 'gateway_client',
           'gateway_helpers', 'controllers', 'master', 'sample_utilization',
           'scope', 'transmitters', 'always_on', 'ivi',
           '__version__']


# Uncomment when deploying pip package
def main():
    """kicks off client"""
    always_on.run()
