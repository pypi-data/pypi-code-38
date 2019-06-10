"""check - check that dependencies were added to the virtual environment"""

import os
import subprocess
import caos.common
from caos._internal import update as update_module
from caos._internal.exceptions import (
    VenvNotFound, VenvBinariesMissing, InvalidJSON, MissingJSONKeys,
    InvalidVersionFormat, MissingDependencies
)

_console_messages={
    "success":"Success: The virtual environment has all dependencies installed.",
    "missing_dependencies":"Fail: The virtual environment is missing some dependencies.",
    "fail":"Fail: The check of dependencies could not be made.",
    "permission_error": "Fail: The check command could not run due to permission errors.",
}


def _check_installed_dependencies(json_data:dict) ->list:
    installed_packages_str = subprocess.check_output(
        [os.path.abspath(path=caos.common.constants._PYTHON_PATH), '-m', 'pip', 'freeze']
    )
    installed_packages_list = [r.decode().split('==')[0].lower() for r in installed_packages_str.split()]
    not_installed_packages = []
    for package in json_data[caos.common.constants._CAOS_JSON_REQUIRE_KEY].keys():
        if package.lower() not in installed_packages_list and package.lower() != "pip":
            not_installed_packages.append(package)
    return not_installed_packages


def execute_check(is_unittest: bool = False) -> None:
    try:
        if not update_module._json_exists():
            raise FileNotFoundError()

        if not update_module._venv_exists():
            raise VenvNotFound()

        if not update_module._are_venv_binaries_available():
            raise VenvBinariesMissing()

        json_data = update_module._read_json_file()  # Raise InvalidJSON

        if not update_module._is_json_syntax_correct(json_data=json_data):
            raise MissingJSONKeys()

        if not update_module._are_packages_versions_format_valid(json_data=json_data):
            raise InvalidVersionFormat()

        not_installed_packages = _check_installed_dependencies(json_data=json_data)

        if not_installed_packages:
            print("Dependencies not installed: {0}".format(str(not_installed_packages)[1:-1]))
            raise MissingDependencies()

        print(_console_messages["success"])

    except FileNotFoundError:
        print(update_module._console_messages["no_json_found"])
    except VenvNotFound:
        print(update_module._console_messages["no_venv_found"])
    except VenvBinariesMissing:
        print(update_module._console_messages["missing_venv_binaries"])
    except InvalidJSON:
        print(update_module._console_messages["invalid_json"])
    except MissingJSONKeys:
        print(update_module._console_messages["json_mising_keys"])
    except InvalidVersionFormat:
        print(update_module._console_messages["version_format_error"])
    except MissingDependencies:
        print(_console_messages["missing_dependencies"])
    except PermissionError:
        print(_console_messages["permission_error"])
    except Exception:
        print(_console_messages["fail"])