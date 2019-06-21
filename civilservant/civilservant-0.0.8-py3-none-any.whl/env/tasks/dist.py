import shutil
from pathlib import Path

from invoke import task

from ..pipenv import Pipenv

PROJECT_ROOT_PATH = Path(__file__).parents[3]
PROJECT_BUILD_PATH = Path(PROJECT_ROOT_PATH, "build")
PROJECT_EGG_PATH = Path(PROJECT_ROOT_PATH, "civilservant.egg-info")
PROJECT_DIST_PATH = Path(PROJECT_ROOT_PATH, "dist")
PYPI_URL_PROD = "https://upload.pypi.org/legacy/"
PYPI_URL_TEST = "https://test.pypi.org/legacy/"


@task
def clean(c, build=True, dist=True, egg=False):
    """Clean out build folders and files."""
    if build and PROJECT_BUILD_PATH.exists():
        shutil.rmtree(PROJECT_BUILD_PATH)
    if dist and PROJECT_DIST_PATH.exists():
        shutil.rmtree(PROJECT_DIST_PATH)
    if egg and PROJECT_EGG_PATH.exists():
        shutil.rmtree(PROJECT_EGG_PATH)
    

@task(pre=[clean])
def build(c, source=True, binary=True):
    """Build the latest version of the loader for distribution."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()

    sdist_arg = "sdist" if source else ""
    binary_arg = "bdist_wheel" if binary else ""
    pipenv.run(f"python3 setup.py {sdist_arg} {binary_arg}")


@task
def publish(c, prod=False):
    """Publish the latest version of the loader to PyPI."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()

    url = PYPI_URL_PROD if prod else PYPI_URL_TEST
    dist_files = Path(PROJECT_DIST_PATH, "*")
    pipenv.run(f"twine upload --repository-url {url} {str(dist_files)}")

