"""Auto Key int sequence module
"""
from core_module_auto_key_app.views.views import AutoKeyModule


def generate_int_sequence(values):
    """ Return next integer value

    Args:
        values:

    Returns:

    """
    return 1 if len(values) == 0 else int(max(values)) + 1


class AutoKeyIntModule(AutoKeyModule):
    """ Integer Sequence auto key module
    """

    def __init__(self):
        """
        """
        AutoKeyModule.__init__(self, generate_int_sequence)
