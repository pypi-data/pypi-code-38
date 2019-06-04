from __future__ import print_function
from __future__ import division

import dateutil.parser
import civis


def get_most_recent_run(scriptid, client=None):
    """Get the most recent run of a container script.

    Parameters
    ----------
    scriptid : int
        The ID of the container script.
    client : None or civis.APIClient, optional
        A Civis API client to use. If not given, one will be
        instantiated.

    Returns
    -------
    runid : int
        The ID of the latest run.
    """
    client = client or civis.APIClient(resources='all')

    # First get all of the runs.
    runs = client.scripts.list_containers_runs(scriptid)

    if len(runs) > 0:
        # Get the most recent one.
        run_times = [dateutil.parser.parse(r['finished_at'] or r['started_at'])
                     for r in runs]
        run = runs[run_times.index(max(run_times))]
        return int(run['id'])
    else:
        return None
