"""init - Create the .json template file for the project"""

import os
import caos.common.constants
from caos._internal.templates.caos_json import example_template

_console_messages={
    "success":"Success: caos.json created.",
    "fail": "Fail: caos.json could not be created.",
    "file_exists": "Fail: caos.json already exists.",
    "permission_error": "Fail: caos.json could not be created due to permission errors.",
}


def create_json(is_unittest:bool = False):
    try:
        exists = os.path.isfile(path=caos.common.constants._CAOS_JSON_FILE)
        if exists:
            raise FileExistsError()

        with open(file=caos.common.constants._CAOS_JSON_FILE, mode="w") as caos_json_file:
            caos_json_file.write(example_template)
        print(_console_messages["success"])
    except FileExistsError:
        print(_console_messages["file_exists"])
    except PermissionError:
        print(_console_messages["permission_error"])
    except Exception:
        print(_console_messages["fail"])