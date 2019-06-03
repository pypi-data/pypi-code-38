import logging
import os
import requests
from .print_or_log import print_update_info

conda_timeout_seconds = 3.0

logger = logging.getLogger('missinglink')


def is_conda_env():
    return os.environ.get('CONDA_DEFAULT_ENV') is not None


def get_conda_channel(staging):
    return 'missinglink.ai' if not staging else 'missinglink-test'


def get_latest_conda_version(package, staging, throw_exception=False):
    try:
        channel = get_conda_channel(staging)
        url = 'https://api.anaconda.org/package/{channel}/{package}'.format(channel=channel, package=package)
        r = requests.get(url, timeout=conda_timeout_seconds)
        r.raise_for_status()

        package_info = r.json()
        versions = package_info['versions']
        max_ver = max(versions, key=lambda v: tuple(int(t) for t in v.split('.')))

        print_update_info('latest conda version %s (staging version: %s))', max_ver, staging)

        return max_ver
    except Exception as e:
        if throw_exception:
            raise

        logger.exception('could not check for new missinglink-sdk version:\n%s', e)
        return None


# noinspection PyBroadException
def conda_install(staging, require_package, pipe_streams=True):
    from subprocess import Popen, PIPE

    channel = get_conda_channel(staging)

    env_name = os.environ.get('CONDA_DEFAULT_ENV')
    conda_exe = os.environ.get('CONDA_EXE', 'conda')
    args = [conda_exe, 'install', '-n', env_name, '-c', channel, '--update-deps', '-y', require_package]
    try:
        print_update_info('conda install => %s', ' '.join(args))
        pipe_streams = PIPE if pipe_streams else None
        return Popen(args, stdin=pipe_streams, stdout=pipe_streams, stderr=pipe_streams), args
    except Exception:
        logger.exception("%s failed", " ".join(str(a) for a in args))
        return None, args
