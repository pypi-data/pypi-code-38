from __future__ import print_function
from __future__ import division

import os
import sys
from civis.compat import TemporaryDirectory

import yaml
import civis

from .defaults import LASTSCRIPTID_LOC
from .parsing import _parse_options_from_file, _process_options
from .notebooks import _reformat_notebook
from .caching import FileIDCache


def _upload_files(files, use_cache):
    """Upload file(s) to files endpoint.

    Parameters
    ----------
    files : list of str
        List of files to upload.
    use_cache : bool
        If True, cache the file IDs locally. Otherwise files will
        always be uploaded.

    Returns
    -------
    fileids : dict
        Dictionary mapping file names to Civis Platform file IDs as strings.
    """
    if use_cache:
        cache = FileIDCache()

    fileids = {}
    for fname in files:
        if use_cache:
            fileid = cache.get_fileid(fname)
        else:
            with open(fname, 'rb') as fp:
                fileid = civis.io.file_to_civis(fp, 'file')
        fileids[fname] = str(fileid)
    return fileids


def _build_container_cmd(
        script, remote_script, cli_args, fileids, repo_cmd, shell_cmd):
    """Build the docker command.

    Parameters
    ----------
    script : str
        The /path/to/the/script.XXX or a shell command.
    remote_script : str
        The path to put the script in the container. This could differ
        from the local path for notebooks since they are reformatted
        locally before being executed.
    cli_args : list
        List of arguments from the command line.
    fileids : dict
        Dictionary mapping file names to file IDs.
    repo_cmd : str or None
        Command to use to install the cloned repo in the container. If None
        no repo is installed.
    shell_cmd : str or None
        A shell command to execute before the repo is installed (possibly)
        and after all files from the file IDs are downloaded to the
        container.

    Returns
    -------
    cmd : str
        The command to run in docker.
    """
    container_cmd = []

    container_cmd.append(
        "export CIVIS_JOB_DATA="
        "/data/civis_job_data_${CIVIS_JOB_ID}_${CIVIS_RUN_ID}")
    container_cmd.append("mkdir -p ${CIVIS_JOB_DATA}")

    for fname, fileid in fileids.items():
        pth = os.path.dirname(fname)
        if len(pth) > 0:
            container_cmd.append("mkdir -p %s" % pth)
        container_cmd.append("civis files download %s %s" % (fileid, fname))

    if shell_cmd:
        container_cmd.append(shell_cmd)

    if repo_cmd:
        container_cmd.append("cd /app && %s && cd .." % repo_cmd)

    if os.path.isfile(script):
        container_cmd.append("chmod a+rwx %s" % remote_script)

        if script.endswith('.py'):
            cmd = 'python'
        elif script.endswith('.ipynb'):
            # Set ipython to not output color so container logs are readable.
            cmd = "ipython --InteractiveShell.colors='nocolor'"
        elif script.endswith('.r') or script.endswith('.R'):
            cmd = ('Rscript --default-packages=methods,datasets,'
                   'utils,grDevices,graphics,stats')
        else:
            cmd = 'sh'

        cstr = "%s %s" % (cmd, remote_script)
    else:
        cstr = script
    container_cmd.append(" ".join([cstr] + list(cli_args)))

    container_cmd.append("echo \"Job Output:\"")
    container_cmd.append("tar -czvf ${CIVIS_JOB_DATA}.tar.gz -C /data "
                         "civis_job_data_${CIVIS_JOB_ID}_${CIVIS_RUN_ID}")
    container_cmd.append(
        'if [ "$(ls -A ${CIVIS_JOB_DATA})" ]; then \\\n'
        '  civis scripts post-containers-runs-outputs '
        '${CIVIS_JOB_ID} ${CIVIS_RUN_ID} \\\n'
        '  `civis files upload ${CIVIS_JOB_DATA}.tar.gz` File; \\\nfi')

    return " && \\\n".join(container_cmd)


def _print_job(req, container_cmd, docker_image, params):
    """Print information about a container."""
    pdict = {}
    pdict.update(params)
    pdict['docker_image_name'] = docker_image
    pdict['required_resources'] = req

    print('container script config:')
    for line in yaml.dump(pdict, default_flow_style=False).split('\n'):
        if len(line) > 0:
            print('  ' + line)

    print('container script cmd:')
    for line in container_cmd.split('\n'):
        print('  ' + line)


def _post_and_run_job(req, container_cmd, docker_image, params, client):
    """Make and run a container. Returns the ID of the container."""

    try:
        jobid = client.scripts.post_containers(
            req, container_cmd, docker_image, **params)['id']
    except civis.base.CivisAPIError as e:
        print(
            "Could not create container: %s.%s: %s" % (
                e.__module__, e.__class__.__name__, e), file=sys.stderr)
        sys.exit(-1)

    try:
        client.scripts.post_containers_runs(jobid)
    except civis.base.CivisAPIError as e:
        print(
            "Could not run container %s: %s.%s: %s" % (
                jobid, e.__module__, e.__class__.__name__, e), file=sys.stderr)
        sys.exit(-1)

    return jobid


def _record_last_jobid(jobid):
    """Save the last jobid."""
    lid_name = os.path.expandvars(os.path.expanduser(LASTSCRIPTID_LOC))
    lid_path = os.path.split(lid_name)[0]
    if not os.path.exists(lid_path):
        os.makedirs(lid_path)
    try:
        with open(lid_name, 'w') as fp:
            fp.write('%d\n' % jobid)
    except Exception:
        pass


def _sub_job(script, remote_script, cli_args, cli_params, client, dry_run):
    """Submit a container job via the CLI.

    Parameters
    ----------
    script : str
        The local path to the script or a shell command.
    remote_script : str
        The path to put the script in the container. This could differ
        from the local path for notebooks since they are reformatted
        locally before being executed.
    cli_args : list or None
        A list of command line arguments.
    cli_params : dict
        A dictionary of command line options.
    client : civis.APIClient
        An API client instance to use.
    dry_run : bool
        If True, print info about the script and do not submit it.

    Returns
    -------
    jobid : int or None
        The ID of the script. None is returned if no script is submitted.
    """

    # Set cli_args.
    cli_args = cli_args or []

    # Get parameters.
    if os.path.isfile(script):
        with open(script, 'r') as fp:
            params = _parse_options_from_file(fp)
    else:
        params = {}

    if script.endswith('.r') or script.endswith('.R'):
        script_type = 'r'
    else:
        script_type = 'python'

    params = _process_options(params, script_type, cli_params, client)

    # Upload the files.
    otherfiles = params.pop('files', [])
    for arg in cli_args:
        if os.path.isfile(arg):
            otherfiles.append(arg)
    if os.path.isfile(script):
        otherfiles.append(script)

    use_cache = params.pop('use_file_cache')
    if not dry_run:
        fileids = _upload_files(
            otherfiles,
            use_cache)
    else:
        # some dummy IDs
        fileids = dict(zip(otherfiles, range(len(otherfiles), -1, -1)))

    # Make sure to handle the path correctly for reformatted things.
    if os.path.isfile(script) and remote_script != script:
        fileids[remote_script] = fileids[script]
        del fileids[script]

    # Now create container job submission string.
    repo_cmd = params.pop('repo_cmd', None)
    shell_cmd = params.pop('shell_cmd', None)
    container_cmd = _build_container_cmd(
        script,
        remote_script,
        cli_args,
        fileids,
        repo_cmd if 'repo_http_uri' in params else None,
        shell_cmd)

    # Final steps.
    req = params.pop('required_resources')
    docker_image = params.pop('docker_image_name')
    if dry_run:
        _print_job(req, container_cmd, docker_image, params)
        jobid = None
    else:
        jobid = _post_and_run_job(
            req, container_cmd, docker_image, params, client)

    return jobid


def _sub(script, cli_args, cli_params):
    """Driver for the CLI submit command"""
    client = civis.APIClient(resources='all')
    dry_run = cli_params.pop('dry_run')

    if os.path.isfile(script) and script.endswith('.ipynb'):
        # Make notebooks python scripts in temp dir
        with TemporaryDirectory() as tmpdir:
            new_script = os.path.join(tmpdir, os.path.basename(script))

            with open(new_script, 'w') as fp:
                fp.write(_reformat_notebook(script))

            jobid = _sub_job(
                new_script,
                script,
                cli_args,
                cli_params,
                client,
                dry_run)
    else:
        jobid = _sub_job(
            script, script, cli_args, cli_params, client, dry_run)

    if jobid:
        print(jobid)

        # If we get here, stuff the script ID in the user's home
        # area for later.
        _record_last_jobid(jobid)
