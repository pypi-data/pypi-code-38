"""test - run the unit tests from the configured test folder using the virtual environment"""

import os
import subprocess
import caos.common
from caos._internal import update as update_module
from caos._internal.exceptions import (
    VenvNotFound, VenvBinariesMissing, InvalidJSON, MissingJSONKeys,
    InvalidVersionFormat, InvalidTestsPath
)

_console_messages={
    "success":"Success: All tests were executed.",
    "fail": "Fail: Tests could not be executed.",
    "missing_tests": "Fail: The path inside caos.json for running tests does not exist.",
    "permission_error": "Fail: Tests could not be executed due to permission errors.",
}


def _tests_folder_exists(json_data:dict) -> bool:
    exists = os.path.isdir(json_data[caos.common.constants._CAOS_JSON_TESTS_KEY])
    if exists:
        return True
    else:
        return False


def _execute_unittests(tests_path:str ,is_unittest:bool = False) -> None:
    if is_unittest:
        process=subprocess.run(
            [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "unittest", "discover", os.path.abspath(path=tests_path)],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(process.stdout)
        print(process.stderr)
        return
    

    process=subprocess.run(
        [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "unittest", "discover", os.path.abspath(path=tests_path)]
    )


def run_tests(is_unittest:bool = False) -> None:
    try:
        if not update_module._json_exists():            
            raise FileNotFoundError()
        
        if not update_module._venv_exists():            
            raise VenvNotFound()        

        if not update_module._are_venv_binaries_available():
            raise VenvBinariesMissing()
        
        json_data = update_module._read_json_file() # Raise InvalidJSON

        if not update_module._is_json_syntax_correct(json_data=json_data):
            raise MissingJSONKeys()
        
        if not update_module._are_packages_versions_format_valid(json_data=json_data):
            raise InvalidVersionFormat()

        if not _tests_folder_exists(json_data=json_data):
                raise InvalidTestsPath()
        
        _execute_unittests(tests_path=json_data[caos.common.constants._CAOS_JSON_TESTS_KEY], is_unittest=is_unittest)   

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
    except InvalidTestsPath:
        print(_console_messages["missing_tests"])
    except PermissionError:
        print(_console_messages["permission_error"])
    except Exception:
        print(_console_messages["fail"])