import os
import imp

version = "0.1"


def imp_module_with_dot(path, module_name, file=None):
    if not os.path.isfile(path):
        if file is None:
            raise ValueError(
                "when `path` is not a file, must pass `__file__` varaible as argument `file`"
            )
        path = os.path.join(get_root_dir(file), path)
    with open(path, "rb") as fp:
        return imp.load_module(module_name, fp, path, (".py", "rb", imp.PY_SOURCE))


def get_root_dir(__file__):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)))
