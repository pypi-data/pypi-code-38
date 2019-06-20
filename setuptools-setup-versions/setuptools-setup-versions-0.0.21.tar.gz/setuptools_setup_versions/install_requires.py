import re, pkg_resources
from warnings import warn

from . import find, parse

try:
    from collections import Sequence, Optional
except ImportError:
    Sequence = Optional = None


def update_versions(package_directory_or_setup_script=None, operator=None):
    # type: (Optional[str], Optional[str]) -> bool
    """
    Update setup.py installation requirements to (at minimum) require the
    version of each referenced package which is currently installed.

    Parameters:

        package_directory_or_setup_script (str):

            The directory containing the package. This directory must include a
            file named "setup.py".

    Returns:

         `True` if changes were made to setup.py, otherwise `False`
    """

    setup_script_path = find.setup_script_path(
        package_directory_or_setup_script
    )

    # Read the current `setup.py` configuration
    with parse.SetupScript(setup_script_path) as setup_script:

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

                    # Determine the package version currently installed for this
                    # resource
                    try:
                        version = parse.get_package_version(
                            referenced_package_name
                        )
                    except pkg_resources.DistributionNotFound:
                        missing_packages.append(referenced_package_name)

                    if package_operator:
                        install_requires.append(
                            referenced_package + package_operator + version
                        )
                    else:
                        install_requires.append(referenced_package)

                setup_call['install_requires'] = install_requires

                if missing_packages:
                    warn(
                        'The following packages were not present in the source '
                        'environment, and therefore a version '
                        'could not be inferred: ' + ', '.join(missing_packages)
                    )

        modified = setup_script.save()

    return modified