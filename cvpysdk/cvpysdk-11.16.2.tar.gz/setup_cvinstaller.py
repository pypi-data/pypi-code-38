# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Setup file for the CVPySDK Python package."""

import os
import re
import sys
import json
import subprocess
import platform

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    """Gets the version of the CVPySDK python package from __init__.py file."""
    init = open(os.path.join(ROOT, 'cvpysdk', '__init__.py')).read()
    return VERSION.search(init).group(1)


def readme():
    """Reads the README.rst file and returns its contents."""
    with open(os.path.join(ROOT, 'README.rst')) as file_object:
        return file_object.read()


def get_license():
    """Reads the LICENSE.txt file and returns its contents."""
    with open(os.path.join(ROOT, 'LICENSE.txt')) as file_object:
        return file_object.read()


# remove previous SDK installations
def remove_previous_versions():
    """Uninstalls the older installed versions of SDK before installing the latest version."""
    for _ in range(5):
        process = subprocess.Popen(
            [PIP_PATH, 'uninstall', '-y', "cvpysdk"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output, error = process.communicate()

        if output:
            print(output.decode())
        else:
            print(error.decode())
            break


INSTALL_PACKAGES = False

if 'win' in sys.platform.lower():
    PYTHON_PATH = sys.executable
    PIP_PATH = os.path.join(os.path.dirname(PYTHON_PATH), 'Scripts', 'pip')
    INSTALL_PACKAGES = True

elif 'os400' in platform.system().lower():
    PIP_PATH = "pip3"
    INSTALL_PACKAGES = True


remove_previous_versions()


setup(
    name='cvpysdk',
    version=get_version(),
    author='Commvault Systems Inc.',
    author_email='Dev-PythonSDK@commvault.com',
    description='Commvault SDK for Python',
    license=get_license(),
    long_description=readme(),
    url='https://github.com/CommvaultEngg/cvpysdk',
    scripts=[],
    packages=find_packages(),
    keywords='commvault, python, sdk, cv, simpana, commcell, cvlt, webconsole',
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Tracker': 'https://github.com/CommvaultEngg/cvpysdk/issues',
        'Documentation': 'https://commvaultengg.github.io/cvpysdk/',
        'Source Code': 'https://github.com/CommvaultEngg/cvpysdk/tree/SP16'
    }
)


def install_dependencies(package):
    """Recursively installs all the dependencies for the SDK required packages, and prints
        their output to the console.

        Args:
            package     (dict)  --  the dictionary consisting of the package wheel file path,
            and the list of all the dependencies for this package

                e.g.; following is the dict for wheel file and list of dependencies for the
                **requests** python package

                {
                    "package": ["requests-2.18.4-py2.py3-none-any.whl"],

                    "dependencies": [

                        {
                            "package": ["certifi-2018.4.16-py2.py3-none-any.whl"],

                            "dependencies": []
                        },
                        {
                            "package": ["chardet-3.0.4-py2.py3-none-any.whl"],

                            "dependencies": []
                        },
                        {
                            "package": ["idna-2.6-py2.py3-none-any.whl"],

                            "dependencies": []
                        },
                        {
                            "package": ["urllib3-1.22-py2.py3-none-any.whl"],

                            "dependencies": []
                        }
                    ]
                }

        Returns:
            None

    """
    if len(package["package"]) == 1:
        package["package"] = package["package"][0]
    else:
        package["package"] = list(
            filter(lambda x: x.startswith(PYTHON_VERSION_FOLDER), package["package"])
        )[0]

    print('\nInstalling the dependencies for the package: "{0}"'.format(package["package"]))

    if package["dependencies"]:
        for dependency in package["dependencies"]:
            print('Processing dependency: "{0}"'.format(dependency["package"]))
            install_dependencies(dependency)

        print("All dependencies processed\nInstalling the package now...\n\n")

    else:
        print("No dependencies found")

    process = subprocess.Popen(
        [
            PIP_PATH,
            'install',
            os.path.join(PACKAGES_DIRECTORY, package["package"]).replace("\\", "/")
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output, error = process.communicate()

    if output:
        print(output.decode())

    elif error:
        print(error.decode())

    else:
        print(output.decode())


if INSTALL_PACKAGES:
    PACKAGES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages')

    with open(os.path.join(PACKAGES_DIRECTORY, 'packages.json')) as PACKAGES_JSON_FILE:
        PACKAGES_JSON = json.load(PACKAGES_JSON_FILE)

    PYTHON_VERSION_FOLDER = 'PY{0}{1}'.format(
        str(sys.version_info.major), str(sys.version_info.minor)
    )

    for PACKAGE in PACKAGES_JSON:
        print('\nInstalling required package: "{0}"\n'.format(PACKAGE))

        install_dependencies(PACKAGES_JSON[PACKAGE])

        print('Installation for package: "{0}" finished successfully\n'.format(PACKAGE))

    print("All packages installed successfully")
