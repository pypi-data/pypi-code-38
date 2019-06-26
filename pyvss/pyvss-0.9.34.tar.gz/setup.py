import codecs
from datetime import datetime as dt
import io
import os
import re

from setuptools import find_packages, setup

# shared consts using approach suggested at
# https://stackoverflow.com/questions/17583443/what-is-the-correct-way-to-share-package-version-with-setup-py-and-the-package


def read(*parts):
    """Read file from current directory."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as infofile:
        return infofile.read()


def find_version(*file_paths):
    """Locate version info to share between const.py and setup.py."""
    version_file = read(*file_paths)  # type: ignore
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(requires_file='requirements.txt'):
    """Load requirements from file"""
    with io.open(requires_file, encoding='utf-8') as f:
        return f.read().splitlines()


__VERSION__ = find_version("pyvss", "const.py")  # type: ignore

REQUIRES = load_requirements()

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

PROJECT_NAME = 'ITS Private Cloud Python Client'
PROJECT_PACKAGE_NAME = 'pyvss'
PROJECT_LICENSE = 'MIT'
PROJECT_AUTHOR = 'University of Toronto'
PROJECT_COPYRIGHT = ' 2019-{0}, {1}'.format(dt.now().year, PROJECT_AUTHOR)
PROJECT_URL = 'https://gitlab-ee.eis.utoronto.ca/vss/py-vss'
PROJECT_DOCS = 'https://eis.utorotno.ca/~vss/py-vss'
PROJECT_EMAIL = 'vss-apps@eis.utoronto.ca'
MAINTAINER_EMAIL = 'vss-py@eis.utoronto.ca'

PROJECT_GITLAB_GROUP = 'vss'
PROJECT_GITLAB_REPOSITORY = 'py-vss'

PYPI_URL = 'https://pypi.python.org/pypi/{0}'.format(PROJECT_PACKAGE_NAME)
GITLAB_PATH = '{0}/{1}'.format(PROJECT_GITLAB_GROUP, PROJECT_GITLAB_REPOSITORY)
GITLAB_URL = 'https://gitlab-ee.eis.utoronto.ca/{0}'.format(GITLAB_PATH)

DOWNLOAD_URL = '{0}/archive/{1}.zip'.format(GITLAB_URL, __VERSION__)
PROJECT_URLS = {
    'Bug Reports': '{0}/issues'.format(GITLAB_URL),
    'Documentation': '{0}/'.format(PROJECT_DOCS),
    'Source': '{0}'.format(PROJECT_URL),
}

TESTS_REQUIRE = [
    'flake8==3.7.7',
    'nose==1.3.7',
    'coverage==4.5.3',
    'pytz==2018.9',
    'wheel==0.33.1',  # Otherwise setup.py bdist_wheel does not work
]
DEV_REQUIRE = [
    'flake8==3.7.7',
    'nose==1.3.7',
    'coverage==4.5.3',
    'pytz==2018.9',
    'wheel==0.33.1',
    'sphinx-rtd-theme==0.4.3',
    'Sphinx==1.8.5',
]

# Allow you to run
# pip install .[test]
# pip install .[dev]
# to get test dependencies included
EXTRAS_REQUIRE = {'test': TESTS_REQUIRE, 'dev': DEV_REQUIRE}

setup(
    name=PROJECT_PACKAGE_NAME,
    version=__VERSION__,
    url=PROJECT_URL,
    download_url=DOWNLOAD_URL,
    project_urls=PROJECT_URLS,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    maintainer_email=MAINTAINER_EMAIL,
    packages=PACKAGES,
    license=PROJECT_LICENSE,
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    tests_require=TESTS_REQUIRE,
)
