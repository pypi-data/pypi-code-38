import os

"""
Rescue Environment Variable from the System
"""

def get_env_variable(var_name):
    #print(var_name)
    try:
        return os.environ.get(var_name, None)
    except Exception as e:
        error_msg = "Set the %s environment variable" % var_name
        raise e

