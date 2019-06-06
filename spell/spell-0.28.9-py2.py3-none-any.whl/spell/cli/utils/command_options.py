from functools import wraps

import click

from spell.cli.utils import LazyChoice, HiddenOption
from spell.cli.api_constants import (
    get_machine_types,
    get_machine_type_default,
)


def dependency_params(include_python_version=True):
    """Creates a decorator for adding run dependency CLI options"""

    def dependency_params_inner(f):
        """Adds run dependency CLI options"""

        @click.option("--pip", "pip_packages",
                      help="Single dependency to install using pip", multiple=True)
        @click.option("--pip-req", "requirements_file",
                      help="Requirements file to install using pip")
        @click.option("--apt", "apt_packages",
                      help="Dependency to install using apt", multiple=True)
        @click.option("--conda-env", cls=HiddenOption)  # deprecated option -- allow it for compatibility
        @click.option("--conda-file",
                      help="Path to conda specification file or YAML environment file",
                      type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
                      default=None)
        @click.option("-e", "--env", "envvars", multiple=True,
                      help="Add an environment variable to the run")
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        if include_python_version:
            wrapper = (click.option("--python2", is_flag=True, help="set python version to python 2"))(wrapper)
            wrapper = (click.option("--python3", is_flag=True,
                       help="set python version to python 3 (default)"))(wrapper)
        return wrapper

    return dependency_params_inner


def workspace_spec_params(f):
    """Adds run workspace specification CLI options"""

    @click.option("-c", "--commit-ref", default="HEAD",
                  help="Git commit hash to run")
    @click.option("--github-url", help="GitHub URL of a repository to run")
    @click.option("--github-ref", help="commit hash, branch, or tag of the repository to pull (default: 'master')")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def machine_config_params(f):
    """Adds run machine configuration CLI options"""

    @click.option("-t", "--machine-type",
                  type=LazyChoice(get_machine_types), default=get_machine_type_default,
                  help="Machine type to run on")
    @click.option("--framework",
                  help="Machine learning framework to use. For a full list of"
                  " available frameworks see https://spell.run/docs/customizing_environments")
    @click.option("-m", "--mount", "raw_resources", multiple=True, metavar='RESOURCE[:MOUNT_PATH]',
                  help="Attach a resource file or directory to the run (e.g., from a run output, public dataset, "
                       "or upload). The resource (specified by a Spell resource path) is required. "
                       "An optional mount path within the container can also be specified, separated by a "
                       "colon from the resource name. If the mount path is omitted, it defaults to the base name "
                       "of the resource (e.g., 'mnist' for 'public/image/mnist'). "
                       "Example: --mount runs/42:/mnt/data")
    @click.option("--local-caching", cls=HiddenOption, is_flag=True, help="enable local caching of attached resources")
    @click.option("--provider", cls=HiddenOption, help="if specified only machines from that provider will be used"
                  " e.g. aws")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def cli_params(f):
    """Adds miscellanous CLI options"""

    @click.option("-f", "--force", is_flag=True,
                  help="Skip interactive prompts")
    @click.option("-v", "--verbose", is_flag=True,
                  help="Print additional information")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def description_param(f):
    """Adds run description CLI option"""

    @click.option("-d", "--description", default=None,
                  help="Description of the run. If unspecified defaults to the current commit message")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def background_option(f):
    """Adds background CLI option"""

    @click.option("-b", "--background", is_flag=True,
                  help="Do not print logs")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def docker_image_option(f):
    """Adds run docker image CLI option"""

    @click.option("--from", "docker_image",
                  help="Dockerfile on docker hub to run from")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def idempotent_option(f):
    """Adds idempotent run option"""

    @click.option("--idempotent", cls=HiddenOption, is_flag=True,
                  help="Use an existing identical run if one is found instead of launching a new one")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
