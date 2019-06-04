"""update - Update and download the virtual environment dependencies according to the json file"""

import os
import re
import json
import subprocess
import caos.common
from caos._internal.exceptions import (
    VenvNotFound, VenvBinariesMissing, InvalidJSON, MissingJSONKeys,
    InvalidVersionFormat, DownloadDependenciesError
)

_console_messages={
    "success":"Success: Virtual environment updated.",
    "fail": "Fail: Virtual environment could not be updated.",
    "no_json_found": "Fail: caos.json does not exist. To create it run 'caos init'.",
    "no_venv_found": "Fail: Virtual environment does not exist. To create it run 'caos prepare'",
    "missing_venv_binaries": "Fail: The virtual environment is missing some binaries. Try creating it again after installing pip and venv first.",
    "invalid_json": "Fail: caos.json is invalid or has syntax errors.",
    "json_mising_keys": "Fail: caos.json is missing the required keys for it to be valid.",
    "version_format_error": "Fail: At least one package inside caos.json has a wrong version format, the valid format is n.n.n",
    "downloading": "In Progress: Downloading dependencies...",
    "download_error": "Fail: There was an error and the dependencies could not be downloaded.",
    "permission_error": "Fail: Virtual environment could not be updated due to permission errors.",
}


def _json_exists() -> bool:
    exists = os.path.isfile(path=caos.common.constants._CAOS_JSON_FILE)
    return True if exists else False


def _venv_exists() -> bool:
    exists = os.path.isdir(caos.common.constants._CAOS_VENV_DIR)
    return True if exists else False


def _are_venv_binaries_available() -> bool:
    exists_python = os.path.isfile(path=caos.common.constants._PYTHON_PATH)
    exists_pip = os.path.isfile(path=caos.common.constants._PIP_PATH)
    exists_activate = os.path.isfile(path=caos.common.constants._ACTIVATE_PATH)
    return exists_python and exists_pip and exists_activate


def _read_json_file() -> dict:
    try:
        with open(file=caos.common.constants._CAOS_JSON_FILE, mode="r") as json_file:  
            return json.load(json_file)
    except Exception:
        raise InvalidJSON()


def _is_json_syntax_correct(json_data:dict) -> bool:
    all_keys_exist = set(caos.common.constants._CAOS_JSON_KEYS).issubset(json_data)
    if all_keys_exist:
        return True
    return False

def _are_packages_versions_format_valid(json_data:dict) -> bool:
    for version in json_data[caos.common.constants._CAOS_JSON_REQUIRE_KEY].values():        
        match_pattern= False
        for pattern in caos.common.constants._CAOS_JSON_PACKAGE_VERSION_PATTERNS:
            if re.match(pattern, version):
                match_pattern = True
                break 
        if match_pattern or version in caos.common.constants._CAOS_JSON_PACKAGE_VALID_VERSIONS:
            return True
    return False


def _download_and_updated_packages(json_data:dict, is_unittest:bool = False) -> None:
    packages = []
    for p, v in json_data[caos.common.constants._CAOS_JSON_REQUIRE_KEY].items():
        if v == caos.common.constants._CAOS_LATEST_VERSION:
            package = p          
        else:
            package = "{0}=={1}".format(p,v)

        packages.append(package)
    
    if is_unittest:
        download_dependencies_process = subprocess.run(
            [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "pip", "install", "--force-reinstall", "pip"] + packages,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE     
        )
        print(download_dependencies_process.stdout)
        print(download_dependencies_process.stderr)
        return
    
    download_dependencies_process = subprocess.run(
        [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "pip", "install", "--force-reinstall", "pip"] + packages
    )


def update_dependencies(is_unittest:bool = False) -> None:
    try:
        if not _json_exists():            
            raise FileNotFoundError()
        
        if not _venv_exists():            
            raise VenvNotFound()        

        if not _are_venv_binaries_available():
            raise VenvBinariesMissing()
        
        json_data = _read_json_file() # Raise InvalidJSON

        if not _is_json_syntax_correct(json_data=json_data):
            raise MissingJSONKeys()
        
        if not _are_packages_versions_format_valid(json_data=json_data):
            raise InvalidVersionFormat()              
        
        print(_console_messages["downloading"])
        _download_and_updated_packages(json_data=json_data, is_unittest=is_unittest)
        
    except FileNotFoundError:
        print(_console_messages["no_json_found"])
    except VenvNotFound:
        print(_console_messages["no_venv_found"])
    except VenvBinariesMissing:
        print(_console_messages["missing_venv_binaries"])
    except InvalidJSON:
        print(_console_messages["invalid_json"])
    except MissingJSONKeys:
        print(_console_messages["json_mising_keys"])
    except InvalidVersionFormat:
        print(_console_messages["version_format_error"])
    except DownloadDependenciesError:
        print(_console_messages["download_error"])
    except PermissionError:
        print(_console_messages["permission_error"])
    except Exception:
        print(_console_messages["fail"])