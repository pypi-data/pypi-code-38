class Option:
    """Description of a single configurable option.

    Args:
        name: The name of the option, i.e. its key in the config.
        description: Description of the option.
        default: Default value of the option.
    """
    def __init__(self, name, description, default):
        self._name = name
        self._description = description
        self._default = default

    @property
    def name(self):
        "The name of the option."
        return self._name

    @property
    def description(self):
        "The description of the option."
        return self._description

    @property
    def default(self):
        "The default value of the option."
        return self._default
