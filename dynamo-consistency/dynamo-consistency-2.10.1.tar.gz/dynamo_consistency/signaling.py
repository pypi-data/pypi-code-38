"""
A small module for handling signals
"""

import logging

from . import config
from . import summary


LOG = logging.getLogger(__name__)


def halt(signum, _):
    """
    Halts the current listing using the summary tables
    """

    LOG.warning('Received signal %i. Terminating', signum)

    # If disabled, leave alone

    status = summary.get_status(config.SITE)

    LOG.debug('Site %s status is %i', config.SITE, status)

    if status != summary.DISABLED:
        summary.set_status(config.SITE, summary.HALT)
