import os

import re, pkg_resources, pip
import shutil
import sys
from subprocess import getstatusoutput
from warnings import warn

from . import find, parse

try:
    from collections import Sequence, Optional
except ImportError:
    Sequence = Optional = None


def find_egg_info(directory):
    # type: (str) -> Optional[str]
    egg_info_directory_path = None
    for sub_directory in os.listdir(directory):
        if sub_directory[-9:] == '.egg-info':
            path = os.path.join(directory, sub_directory)
            if os.path.isdir(path):
                egg_info_directory_path = path
                break
    return egg_info_directory_path


def get_package_name_and_version_from_egg_info(directory):
    # type: (str) -> Tuple[Optional[str], Optional[str]]
    """
    Parse the egg's PKG-INFO and return the package name and version
    """

    name = None  # type: Optional[str]
    version = None  # type: Optional[str]
    pkg_info_path = os.path.join(directory, 'PKG-INFO')

    with open(pkg_info_path, 'r') as pkg_info_file:
        for line in pkg_info_file.read().split('\n'):
            if ':' in line:
                property_name, value = line.split(':')[:2]
                property_name = property_name.strip().lower()
                if property_name == 'version':
                    version = value.strip()
                    if name is not None:
                        break
                elif property_name == 'name':
                    name = value.strip()
                    if version is not None:
                        break

    return name, version


def get_package_name_and_version_from_setup(path):
    # type: (str) -> str

    package_name = None  # type: Optional[str]
    version = None  # type: Optional[str]

    # Get the current working directory
    current_directory = os.path.abspath(os.curdir)

    # Change directory to the setup script's directory
    os.chdir(os.path.dirname(path))

    directory = os.path.dirname(path)

    egg_info_directory = find_egg_info(directory)

    if egg_info_directory:

        package_name, version = get_package_name_and_version_from_egg_info(egg_info_directory)

    else:

        # Execute the setup script
        command = '%s %s egg_info' % (sys.executable, path)
        status, output = getstatusoutput(command)

        if status:
            raise OSError(output)

        egg_info_directory = find_egg_info(directory)

        if egg_info_directory:
            package_name, version = get_package_name_and_version_from_egg_info(egg_info_directory)
            shutil.rmtree(egg_info_directory)

    # Restore the previous working directory
    os.chdir(current_directory)

    return package_name, version


def get_package_version(package_name):
    # type: (str) -> str
    normalized_package_name = package_name.replace('_', '-')
    try:
        version = pkg_resources.get_distribution(normalized_package_name).version
    except pkg_resources.DistributionNotFound:
        # The package has no distribution information setup--obtain it from `setup.py`
        for entry in pkg_resources.working_set.entries:
            setup_script_path = entry + '/setup.py'
            if os.path.exists(setup_script_path):
                name, version_ = get_package_name_and_version_from_setup(setup_script_path)
                if name.replace('_', '-') == normalized_package_name:
                    version = version_
                    break
    return version


def update_versions(package_directory_or_setup_script=None, operator=None):
    # type: (Optional[str], Optional[str]) -> bool
    """
    Update setup.py installation requirements to (at minimum) require the version of each referenced package which is
    currently installed.

    Parameters:

        package_directory_or_setup_script (str):

            The directory containing the package. This directory must include a file named "setup.py".

    Returns:

         `True` if changes were made to setup.py, otherwise `False`
    """

    setup_script_path = find.setup_script_path(package_directory_or_setup_script)

    with parse.SetupScript(setup_script_path) as setup_script:  # Read the current `setup.py` configuration

        for setup_call in setup_script.setup_calls:

            if 'install_requires' in setup_call:

                install_requires = []
                missing_packages = []

                for requirement in setup_call['install_requires']:

                    # Parse the requirement string
                    parts = re.split(r'([<>=]+)', requirement)

                    if len(parts) == 3:  # The requirement includes a version
                        referenced_package, package_operator, version = parts
                        if operator:
                            package_operator = operator
                    else:  # The requirement does not yet include a version
                        referenced_package = parts[0]
                        if '@' in referenced_package:
                            package_operator = version = None
                        else:
                            package_operator = operator
                            version = '0' if operator else None

                    referenced_package_name = referenced_package.split('@')[0]

                    # Determine the package version currently installed for this resource
                    try:
                        version = get_package_version(referenced_package_name)
                    except pkg_resources.DistributionNotFound:
                        missing_packages.append(referenced_package_name)

                    if package_operator:
                        install_requires.append(referenced_package + package_operator + version)
                    else:
                        install_requires.append(referenced_package)

                setup_call['install_requires'] = install_requires

                if missing_packages:
                    warn(
                        'The following packages were not present in the source environment, and therefore a version ' +
                        'could not be inferred: ' + ', '.join(missing_packages)
                    )

        modified = setup_script.save()

    return modified