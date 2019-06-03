import click
import semver
import requests

from .version import version as story_version
from .storage import cache

PYPI_API_URL = 'https://pypi.org/pypi/story/json'
CACHE_EXPIRES = 60 * 60 * 3
REQUEST_TIMEOUT = 2

http_session = requests.Session()


def _latest_pypi():
    # Restore from cache, if applicable.
    if 'cli-latest' in cache:
        return cache['cli-latest']

    # Make an HTTP request to the PyPI JSON API.
    try:
        r = http_session.get(url=PYPI_API_URL, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
    except Exception:
        return None

    # Fetch the releases from the JSON response.
    releases = r.json()['releases']

    # Grab the latest release.
    latest = [k for k in releases.keys()][-1]

    # Store the results in the cache for three hours.
    cache.store('cli-latest', latest, expires=CACHE_EXPIRES)

    # Parse the version string.
    return latest


def ensure_latest():
    current_version = '.'.join(story_version.split('.')[:3])

    # Grab the latest version from PyPi. Valid for three hours.
    latest_version = _latest_pypi()

    if latest_version:
        if semver.cmp(current_version, latest_version) == -1:
            click.echo(
                click.style(
                    f'A new release (v{latest_version}) of the Storyscript ClI is now available!',
                    fg='yellow',
                ),
                err=True,
            )
