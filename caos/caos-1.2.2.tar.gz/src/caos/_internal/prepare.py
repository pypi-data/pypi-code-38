"""prepare - Create and prepare the virtual environment for the project"""

import os
import sys
import subprocess
import caos.common.constants
from caos._internal.exceptions import VenvExistsError

_console_messages={
    "success":"Success: Virtual environment created.",
    "fail": "Fail: Virtual environment could not be created.",
    "venv_exists": "Fail: Virtual environment folder already exists.",
    "permission_error": "Fail: Virtual environment could not be created due to permission errors.",
}


def create_venv(is_unittest:bool = False) -> int:
    try:
        exists = os.path.isdir(caos.common.constants._CAOS_VENV_DIR)
        if exists:
            raise VenvExistsError()

        subprocess.run(
            [os.path.abspath(path=sys.executable), "-m", "venv", "venv"]
        )

        print(_console_messages["success"])
        return 0
    except VenvExistsError:
        print (_console_messages["venv_exists"])
        return 1
    except PermissionError:
        print(_console_messages["permission_error"])
        return 1
    except Exception:
        print(_console_messages["fail"])
        return 1