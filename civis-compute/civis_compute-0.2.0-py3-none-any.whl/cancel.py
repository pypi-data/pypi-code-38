from __future__ import print_function
from __future__ import division

import sys
import civis


def _cancel(scriptids):
    """Cancel running scripts.

    Parameters
    ----------
    scriptids : tuple of ints
        The IDs of the scripts to cancel.
    """
    errored = False
    client = civis.APIClient(resources='all')
    for scriptid in scriptids:
        try:
            client.scripts.post_cancel(scriptid)
        except civis.base.CivisAPIError as e:
            errored = True
            print(
                "Could not cancel script %s: %s.%s: %s" % (
                    scriptid, e.__module__, e.__class__.__name__, e),
                file=sys.stderr)

    if errored:
        sys.exit(-1)
