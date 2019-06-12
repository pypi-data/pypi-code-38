import os as _os


def get_env(var_name, required=True):
    val = _os.getenv(var_name)
    
    if required:
        assert val is not None, \
            "%s environment variable not found." % var_name
    
    return val if val is not None else ""
