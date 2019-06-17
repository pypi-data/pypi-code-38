# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def singleton(_class):
    """ decorator for a class to make a singleton out of it
        Modified from
        http://code.activestate.com/recipes/578103-singleton-parameter-based/ to support one instance of class
     """
    key_to_instance = {}

    def get_instance(*args, **kwargs):
        if "value" not in key_to_instance:
            key_to_instance["value"] = _class(*args, **kwargs)
        return key_to_instance["value"]

    return get_instance
