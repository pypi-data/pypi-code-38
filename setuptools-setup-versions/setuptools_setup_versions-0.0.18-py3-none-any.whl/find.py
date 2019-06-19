import os
import re

from . import install_requires


try:
    from collections import Optional, Tuple, Dict, Any
except ImportError:
    Optional = Tuple = Dict = Any = None


def setup_script_path(package_directory_or_setup_script=None):
    # type: (Optional[str]) -> str
    """
    Find the setup script
    """

    if package_directory_or_setup_script is None:
        setup_script_path = './setup.py'
    elif package_directory_or_setup_script[-9:] == '/setup.py':
        # If we've been passed the setup.py file path, get the package directory
        setup_script_path = package_directory_or_setup_script
    else:
        if os.path.isdir(package_directory_or_setup_script):
            # If we've been passed the package directory, get the setup file path
            setup_script_path = os.path.join(package_directory_or_setup_script, 'setup.py')
        else:
            raise FileNotFoundError(
                '"%s" is not a package directory or setup script.' % package_directory_or_setup_script
            )

    if not os.path.isfile(setup_script_path):
        raise FileNotFoundError(
            'Setup script does not exist: ' + setup_script_path
        )

    return setup_script_path


