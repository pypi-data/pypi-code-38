from __future__ import print_function
from __future__ import division

import os
import sys
import civis

from .utils import get_most_recent_run


def _get(scriptid, runid=None, path=None):
    """Download job data for a script.

    During jobs, civis-compute automatically saves any outputs written
    to the directory given by the environment variable `${CIVIS_JOB_DATA}`.

    The `get` command downloads these outputs if they exist.

    The outputs are stored as a run output with the name

        civis_job_data_${CIVIS_JOB_ID}_${CIVIS_RUN_ID}

    Parameters
    ----------
    scriptid : int
        The container script ID.
    runid : int or None, optional
        The run ID to get outputs for. If None,
        the most recent run is used.
    path : str or None
        The path to download the data to. If None,
        the current working directory is used.
    """
    client = civis.APIClient(resources='all')

    try:
        runid = runid or get_most_recent_run(scriptid, client=client)
        outputs = client.scripts.list_containers_runs_outputs(scriptid, runid)

        for output in outputs:
            if (output['object_type'] == 'File' and
                    'civis_job_data_' in output['name']):

                if path:
                    oname = os.path.join(path, output['name'])
                else:
                    oname = output['name']

                print(oname)

                with open(oname, 'wb') as fp:
                    civis.io.civis_to_file(output['object_id'], fp)

                break
    except civis.base.CivisAPIError as e:
        print(
            "Could not get script %s outputs: %s.%s: %s" % (
                scriptid, e.__module__, e.__class__.__name__, e),
            file=sys.stderr)
        sys.exit(-1)
