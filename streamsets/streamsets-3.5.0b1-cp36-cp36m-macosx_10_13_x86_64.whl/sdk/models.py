# Copyright 2019 StreamSets Inc.

"""Models to be used by multiple StreamSets components."""


class Configuration:
    """Abstraction for stage configurations.

    This class enables easy access to and modification of data stored as a list of dictionaries. As
    an example, SDC's pipeline configuration is stored in the form

    .. code-block:: none

        [ {
          "name" : "executionMode",
          "value" : "STANDALONE"
        }, {
          "name" : "deliveryGuarantee",
          "value" : "AT_LEAST_ONCE"
        }, ... ]

    By implementing simple ``__getitem__`` and ``__setitem__`` methods, this class allows items in
    this list to be accessed using

    .. code-block:: python

        configuration['executionMode'] = 'CLUSTER_BATCH'

    Instead of the more verbose

    .. code-block:: python

        for property in configuration:
            if property['name'] == 'executionMode':
                property['value'] = 'CLUSTER_BATCH'
            break

    Args:
        configuration (:obj:`str`): List of dictionaries comprising the configuration.
        property_key (:obj:`str`, optional): The dictionary entry denoting the property key.
            Default: ``name``
        property_value (:obj:`str`, optional): The dictionary entry denoting the property value.
            Default: ``value``
    """
    def __init__(self, configuration=None, property_key='name', property_value='value', **kwargs):
        # Handle case of a kwarg called ``configuration`` being passed in.
        if isinstance(configuration, str):
            kwargs['configuration'] = configuration
            configuration = None
        if configuration and kwargs:
            raise ValueError('Cannot instantiate Configuration with a list-map and kwargs.')

        if configuration:
            self._data = configuration
        elif kwargs:
            self._data = [{property_key: key, property_value: value}
                          for key, value in kwargs.items()]
        self.property_key = property_key
        self.property_value = property_value

    def items(self):
        """Gets the configuration's items.

        Returns:
            A new view of the configuration’s items ((key, value) pairs).
        """
        # To keep the behavior in line with a Python dict's, we'll generate one and then use its items method.
        configuration_dict = {config_property.get(self.property_key): config_property.get(self.property_value)
                              for config_property in self._data}
        return configuration_dict.items()

    def __getitem__(self, key):
        for config_property in self._data:
            if config_property.get(self.property_key) == key:
                return config_property.get(self.property_value)
        else:
            raise KeyError('Could not find property %s in configuration.', key)

    def __setitem__(self, key, value):
        for config_property in self._data:
            if config_property.get(self.property_key) == key:
                config_property[self.property_value] = value
                break
        else:
            self._data.append({self.property_key: key, self.property_value: value})

    def __contains__(self, item):
        for config_property in self._data:
            if config_property.get(self.property_key) == item:
                return True
        return False

    def get(self, key, default=None):
        """Return the value of key or, if not in the configuration, the default value."""
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, configs):
        """Update instance with a collection of configurations.

        Args:
            configs (:obj:`dict`): Dictionary of configurations to use.
        """
        for key, value in configs.items():
            self[key] = value
