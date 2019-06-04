from __future__ import print_function
from __future__ import division

import yaml

from .defaults import get_defaults


def _parse_options_from_file(fp):
    """Parse job options from comments in a file.

    The comments look like

        #CIVIS name=my job name

    which should get turned into

        {'name': 'my job name'}

    in the output dictionary.

    Parameters
    ----------
    fp : a file-like object
        A file-like object for reading the data from.

    Returns
    -------
    params : dict
        A dictionary of the parsed parameters. If nothing is found,
        an empty dictionary is returned.
    """
    params = {}
    for line in fp.readlines():
        if line[0:6] == '#CIVIS':
            # remove '#CIVIS', split on '=' and then strip out comments
            line = line[6:].strip()
            items = [i.strip() for i in line.split("=", 1)]
            if len(items) == 2:
                items[1] = items[1].split('#')[0].strip()

            if len(items) < 2 or len(items[1]) == 0:
                raise ValueError("civis-compute CLI option must be of form "
                                 "'#CIVIS key = value'!")

            # now parse the results with yaml
            params[items[0]] = yaml.safe_load(items[1])

    return params


def _get_aws_cred_id(client):
    """Get the first AWS credential on platform."""
    name = client.username
    creds = client.credentials.list(type="Amazon Web Services S3")
    for cred in creds:
        if cred['owner'] == name:
            return cred['id']
    raise RuntimeError("Could not get AWS credential ID!")


def _add_aws_creds(params, client):
    """Add the AWS creds to the options.

    Builds a parameter called AWS
    that holds the AWS credentials stored on platform.
    """
    pname = 'AWS'

    if 'params' not in params:
        params['params'] = []

    params['params'].append(
        {'name': pname, 'type': 'credential_aws'})

    if 'arguments' not in params:
        params['arguments'] = {}

    params['arguments'][pname] \
        = params.pop('aws_cred_id', None) or _get_aws_cred_id(client)

    return params


def _cleanup_required_resources(req):
    """Convert tags to ints/floats for required_resources.

    cpu and memory should be ints
    disk_space should be a float
    diskSpace should be disk_space
    """
    for tag in ['cpu', 'memory']:
        req[tag] = int(req[tag])

    # this is always snake_case for inputs...
    if 'diskSpace' in req:
        req['disk_space'] = req['diskSpace']
        del req['diskSpace']

    req['disk_space'] = float(req['disk_space'])

    return req


def _join_container_params(old, new):
    """Join params w/ new updating old.

    This is like

        old.update(new)

    except that the keys

        required_resources
        params
        arguments
        files

    are updated instead of overwritten.

    Parameters
    ----------
    old : dict
        Dictionary of container parameters.
    new : dict
        Dictionary of container parameters.
    """

    old.update({
        k: v for k, v in new.items()
        if k not in ['required_resources', 'params', 'arguments', 'files']})

    # update the dict in old if it is there, otherwise just fill in
    for key in ['required_resources', 'arguments']:
        if key in new:
            if key in old:
                old[key].update(new[key])
            else:
                old[key] = new[key]

    # replace the items in the list by constructing dicts on the
    # name key
    # finally convert back to a list
    if 'params' in new:
        old_pars = {_p['name']: _p for _p in old.get('params', [])}
        old_pars.update({
            _p['name']: _p for _p in new.get('params', [])})
        old['params'] = [_p for _p in old_pars.values()]
        if len(old['params']) == 0:
            del old['params']

    if 'files' in new:
        if 'files' in old:
            old['files'].extend(new['files'])
        else:
            old['files'] = new['files']


def _reformat_files_key(params):
    """Reformat the 'files' key in params.

    Turns instances of the 'files' key as a comma-separated list of file
    names into a Python list of file names.

    The key is deleted if the resulting list of files is empty.

    Parameters
    ----------
    params : dict
    """
    if 'files' in params and isinstance(params['files'], str):
        new_files = params.pop('files', [])
        new_files = [
            i.strip()
            for i in new_files.split(',')
            if len(i.strip()) > 0]
        if new_files:
            params['files'] = new_files


def _process_options(file_params, script_type, cli_params, client):
    """Combine options from defaults, file and command line.

    Parameters
    ----------
    file_params : dict
        Options parsed from the file.
    script_type : str
        The type of script, either 'r' or 'python'.
    cli_params : dict
        Options from the command line.
    client : civis.APIClient
        An API client to use.

    Returns
    -------
    params : dict
        The final set of options.
    """
    # file > defaults always!
    params = get_defaults()
    _reformat_files_key(params)
    params['docker_image_name'] = params['docker_image_name'][script_type]
    if params['repo_cmd'].get(script_type):
        params['repo_cmd'] = params['repo_cmd'][script_type]
    else:
        del params['repo_cmd']
    _reformat_files_key(file_params)
    _join_container_params(params, file_params)

    # CLI > file always!
    # Remove None's to not set weird defaults.
    # click sets things to None if they are not passed, so ignore those
    _cli_params = {k: v for k, v in cli_params.items() if v is not None}
    _reformat_files_key(_cli_params)
    _join_container_params(params, _cli_params)

    # Add AWS credentials as environment variables in the container.
    if params.get('add_aws_creds', False):
        params = _add_aws_creds(params, client)
    params.pop('add_aws_creds', None)
    params.pop('aws_cred_id', None)

    # Cause yeah this happens...
    params['required_resources'] = _cleanup_required_resources(
        params['required_resources'])

    return params
