from importlib import import_module


def import_string(path):
    try:
        module_path, class_name = path.rsplit(".", 1)
    except ValueError:
        raise ImportError("{} doesn't look like a module path".format(path))

    module = import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(
            "Module '{}' does not define a '{}' attribute/class".format(module_path, class_name))

    return True
