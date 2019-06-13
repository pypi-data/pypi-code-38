from setuptools import setup
import re
import os
import codecs
from setuptools import find_packages
here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    version=find_version("middle_auth_client", "__init__.py"),
    name='middle_auth_client',
    description='tools for helping web services and users interact with the middle_auth_service via flask and python',
    author='Chris Jordan',
    author_email='chris@eyewire.org',
    url='https://github.com/seung-lab/middle_auth_client',
    packages=['middle_auth_client'],
    include_package_data=True,
    install_requires=required
)
