from __future__ import print_function
from __future__ import division

import os
import sys

import click
import yaml

from .cancel import _cancel
from .caching import FileIDCache
from .get import _get
from .stat import _status
from .sub import _sub
from .defaults import FILEIDCACHE_FILE


# parameter type for YAML text
class YAMLParamType(click.ParamType):
    """
    A click parameter type for YAML/JSON strings.
    See http://click.pocoo.org/5/parameters/#implementing-custom-types.
    """

    name = 'YAMLTEXT'

    def convert(self, value, param, ctx):
        if value is None:
            return value

        try:
            result = yaml.safe_load(value)
            return result
        except Exception:
            self.fail(
                "Could not load YAML from string: %s" % value, param, ctx)


YAML = YAMLParamType()


@click.group()
def cli():
    """Welcome to the civis-compute command line interface!

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """
    pass


@cli.command()
@click.argument('script')
@click.argument('args', nargs=-1)
@click.option('--name', type=str, help="Name of the container.")
@click.option('--parent-id', type=int,
              help="ID of the parent job that will trigger this script.")
@click.option('--user-context', type=str,
              help='Who to execute the script as when run as a template. '
                   'Either "runner" or "author".')
@click.option('--params', type=YAML,
              help="Definition of the parameters this script accepts in the "
                   "arguments field. See the Civis API docs.")
@click.option('--arguments', type=YAML,
              help="Dictionary of name/value pairs to use to run this script. "
                   "Only settable if this script has defined params. See the "
                   "Civis API docs.")
@click.option('--schedule', type=YAML,
              help="Schedule of when this script will be run. "
                   "See the Civis API docs.")
@click.option('--notifications', type=YAML,
              help="Notifications to send after the script is run. "
                   "See the Civis API docs.")
@click.option('--required-resources', type=YAML,
              help="Resources to allocate for the container. "
                   "This parameter should be set to a string "
                   "with YAML specifying the required "
                   "resources (e.g., \"{'cpu': 2048}\"). "
                   "Possible keys are 'cpu', 'memory' and "
                   "'disk_space'. See the Civis API docs.")
@click.option('--repo-http-uri', type=str,
              help="Location of a github repo to clone into the "
                   "container, e.g. github.com/my-user/my-repo.git.")
@click.option('--repo-ref', type=str,
              help="Tag or branch of the github repo to clone "
                   "into the container.")
@click.option('--remote-host-credential-id', type=int,
              help="ID of the database credentials to pass into "
                   "the environment of the container.")
@click.option('--git-credential-id', type=int,
              help="ID of the git credential to be used when "
                   "checking out the specified git repo. If not "
                   "supplied, the first git credential you've "
                   "submitted will be used. Unnecessary if no "
                   "git repo is specified or the git repo "
                   "is public.")
@click.option('--docker-image-name', type=str,
              help="Name of the docker image to pull from DockerHub.")
@click.option('--docker-image-tag', type=str,
              help="Tag of the docker image to pull from DockerHub. "
                   "(default: latest)")
@click.option('--time-zone', type=str, help="Time zone of this script.")
@click.option('--hidden/--no-hidden', default=None,
              help="Hidden status of the object. Setting this to true hides "
                   "it from most API endpoints. The object can still be "
                   "queried directly by ID")
@click.option('--target-project-id', type=int,
              help="ID of the target project to which script outputs "
                   "will be added.")
@click.option('--cancel-timeout', type=int,
              help="If non-zero, amount of time in seconds to wait between "
                   "sending SIGTERM and SIGKILL to cancel a script. "
                   "Must be in the range 0 to 60.")
@click.option('--files', type=str,
              help="File or comma-separated list of files to upload "
                   "into the container. These files will be placed at "
                   "the same path in the container as they are locally.")
@click.option('--repo-cmd', type=str,
              help="Command to use to process the cloned repo, "
                   "if applicable. (default: `python setup.py install`)")
@click.option('--use-file-cache/--no-use-file-cache', default=None,
              help="Use the local cache of files endpoint IDs to avoid "
                   "duplicate file uploads.")
@click.option('--add-aws-creds/--no-add-aws-creds', default=None,
              help="Add AWS credentials to the submitted script. "
                   "The first AWS credential found is used.")
@click.option('--aws-cred-id', type=int, default=None,
              help="ID of the AWS credential to use when `add-aws-creds` "
                   "is set. If this is not provided, then the first returned "
                   "by the API will be used.")
@click.option('--shell-cmd', type=str,
              help="Shell commands to be executed after all data is "
                   "downloaded to the container but before any other "
                   "installation steps. These can be used to, e.g., install "
                   "packages in a custom way, move data around in the "
                   "container, etc.")
@click.option('--dry-run', is_flag=True,
              help="Configure the container, but do not submit it and "
                   "instead print the configuration.")
def submit(script, args, **kwargs):
    """Submit a SCRIPT to Civis Platform.

    Arguments can be passed directly as ARGS.

    See the Civis API docs

        https://platform.civisanalytics.com/api#v1_post_scripts_containers

    for information about the options.

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """
    _sub(script, args, kwargs)


@cli.command()
@click.argument('scriptids', nargs=-1)
def cancel(scriptids):
    """Cancel Civis Platform container scripts.

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """
    _cancel(scriptids)


@cli.group()
def cache():
    """Manage the cache of file IDs.

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """
    pass


@cache.command()
def list():
    """List items in the file ID cache."""
    fc = FileIDCache()
    fc.list()


@cache.command()
def clear():
    """Clear the file ID cache."""
    fname = os.path.expandvars(os.path.expanduser(FILEIDCACHE_FILE))
    try:
        os.remove(fname)
    except Exception as e:
        print(
            "Could not clear the cache at %s: %s.%s: %s" % (
                    fname, e.__module__, e.__class__.__name__, e),
            file=sys.stderr)
        sys.exit(-1)


@cli.command()
@click.argument('scriptid', nargs=1)
@click.argument('path', type=str, default='.', nargs=1)
@click.option(
    '--run-id',
    'runid',
    type=int,
    help="Get output for a specific run RUN_ID instead of the latest run.")
def get(scriptid, path, runid):
    """Download the outputs for a given SCRIPTID.

    Before the container script finishes running, civis-compute automatically
    saves any outputs written to the directory given by the environment
    variable `${CIVIS_JOB_DATA}` as a Civis Platform file.

    The `get` command downloads these outputs if they exist.

    The most recent run is used unless a run is specified via `--run-id`.

    Optionally download to the given PATH. Otherwise use the current
    working directory.

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """
    _get(scriptid, runid=runid, path=path)


@cli.command()
@click.argument('scriptid', nargs=-1)
@click.option('--mine', '-m', default=False, is_flag=True,
              help="List only your scripts.")
@click.option('--user', type=str, default=None,
              help="List scripts only from this user (or users in a "
                   "comma-separated list).")
@click.option('--runs', default=False, is_flag=True,
              help="List all runs for a given SCRIPTID if SCRIPTID is given.")
@click.option('--run-id', 'runid', type=int, default=None,
              help="List info for a given RUNID if SCRIPTID is given.")
@click.option('--last', '-l', 'last', is_flag=True,
              help="Print details of your last submitted script as if "
                   "you had given it as SCRIPTID.")
@click.option('--hidden', is_flag=True,
              help='List hidden scripts too.')
@click.option('--running', '-r', 'state', flag_value='running', default=True,
              help='List only running scripts. (default)')
@click.option('--all', '-a', 'state', flag_value='all',
              help='List scripts in all states.')
@click.option('--canceled', '-c', 'state', flag_value='canceled',
              help='List only canceled scripts.')
@click.option('--succeeded', '-s', 'state', flag_value='succeeded',
              help='List only succeeded scripts.')
@click.option('--failed', '-f', 'state', flag_value='failed',
              help='List only failed scripts.')
@click.option('--idle', '-i', 'state', flag_value='idle',
              help='List only idle scripts.')
def status(scriptid, mine, user, runs, runid, last, hidden, state):
    """Inspect Civis Platform container scripts.

    Specify SCRIPTID to inspect a given script. Otherwise the status of
    the civis-compute queue will be returned. Only up to ~50 scripts can be
    displayed and only scripts of type "Container" are returned (this includes
    custom and templated scripts).

    Make sure to have your Civis API key in the local environment as
    `CIVIS_API_KEY`.
    """

    _status(
        int(scriptid[0]) if len(scriptid) > 0 else None,
        mine, user, runs, runid, last, hidden, state)
