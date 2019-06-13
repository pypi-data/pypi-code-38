import json
import os

from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)


def get_build_info_path():
    return os.path.join(ROOT, "build_info.json")


BUILD_INFO_PATH = get_build_info_path()


def get_build_info_json():
    with open(BUILD_INFO_PATH) as build_info_file:
        build_info_str = build_info_file.read().strip()
        build_info__json = json.loads(build_info_str)
        return build_info__json


BUILD_INFO_JSON = get_build_info_json()


def get_version():
    version = BUILD_INFO_JSON["version"]
    return version


def get_long_description():
    version = BUILD_INFO_JSON['version']
    # build_url = BUILD_INFO_JSON['build_url']
    branch = BUILD_INFO_JSON['branch']
    changeset = BUILD_INFO_JSON['changeset']
    return open('README.txt').read().format(VERSION=version, BRANCH=branch,
                                            CHANGESET=changeset)  # , BUILD_URL=build_url)


with open('requirements.txt') as f_required:
    requires = f_required.read().splitlines()

setup(
    name="cs18-sidecar",
    author="Quali",
    author_email="support@qualisystems.com",
    description='Sidecar - The CS18 instance',
    long_description=get_long_description(),
    packages=find_packages(exclude=['tests']),
    package_data={'': ['_init_.py', 'logzio.conf']},
    test_suite='nose.collector',
    install_requires=requires,
    version=get_version(),
    include_package_data=True,
    exclude_package_data={'': ['tests']},
    entry_points={
      'console_scripts': ['sidecar=sidecar.sidecar_api:run'],
    },
    classifiers=['Programming Language :: Python :: 3']
)
