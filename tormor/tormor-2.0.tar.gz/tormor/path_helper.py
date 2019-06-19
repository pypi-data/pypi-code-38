from tormor.exceptions import SchemaPathNotFound
import os

def get_schema_path():
    mydir = os.getcwd()
    path = []
    env_schema_path = os.getenv("SCHEMA_PATH")
    if env_schema_path:
        return env_schema_path.split(os.pathsep)
    else:
        for root, dirs, files in os.walk(mydir):
            if "schema" in root.lower() and _check_not_subfolder(path, root):
                path.append(root)
        if not path:
            raise SchemaPathNotFound
        return _check_valid_path(path)

def _check_valid_path(paths):
    valid_path = []
    for each_path in paths:
       if os.path.isdir(each_path):
           valid_path.append(each_path)
    return valid_path

def _check_not_subfolder(main_folders, sub_folders):
    for any_folder in main_folders:
        if any_folder in sub_folders:
            return False
    return True