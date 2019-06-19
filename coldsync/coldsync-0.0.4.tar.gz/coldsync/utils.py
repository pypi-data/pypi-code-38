import os
import re


def make_bucket_name(data_center, project_name, env_name):
    """ Used to create traceable bucket names """
    return re.sub('[^a-zA-Z0-9_\-]+', '_', "-".join([x for x in (data_center, project_name, env_name)]))


def get_from_environment(var_name):
    if var_name not in os.environ:
        raise ValueError("Could not find '%s' in your environment. "
                         "Please provide an environment variable with the same name." % var_name)
    return os.environ[var_name]
