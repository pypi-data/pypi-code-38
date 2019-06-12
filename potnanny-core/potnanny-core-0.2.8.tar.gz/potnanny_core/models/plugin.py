class ActionPluginMount(type):
    """Mount point for ActionPluginBase children."""

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class ActionPluginBase(object, metaclass=ActionPluginMount):
    """All Action Plugins should inherit from this class."""
    pass


class BlePluginMount(type):
    """Mount point for BlePluginBase children."""

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class BlePluginBase(object, metaclass=BlePluginMount):
    """All BLE scanner plugins should inherit from this class."""
    pass
