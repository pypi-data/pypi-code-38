#
#  nn/utils/model.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import copy
from abc import ABC, abstractclassmethod
import json
import torch
import torch.nn as nn
from bxtorch.utils.stdio import ensure_valid_directories

class Config(ABC):
    """
    Base class which standardizes configuration for PyTorch modules.
    """

    # MARK: Static Methods
    @classmethod
    def load(cls, file):
        """
        Loads a configuration from the specified JSON file.

        Parameters:
        -----------
        - file: str
            The full path to the file. The extension does not need to be
            specified, but must be .json.

        Returns:
        --------
        - bxtorch.nn.Config
            The loaded configuration.
        """
        if not file.endswith('.json'):
            file += '.json'
        with open(file, 'r') as f:
            return cls(**json.load(f))

    @abstractclassmethod
    def _parameters(cls):
        """
        Returns the parameters and their optional values than can be specified
        for this configuration.

        Returns:
        --------
        - dict
            A mapping from parameter names to default values. If a parameter
            is required and has no default value, None should be specified.
        """
        pass
    
    # MARK: Initialization
    def __init__(self, **kwargs):
        """
        Initializes a new config from the given parameters.
        """
        all_params = type(self)._parameters()
        params = {}
        keys = set(all_params.keys())

        for k, v in kwargs.items():
            if not k in keys:
                raise ValueError(
                    f'Invalid configuration parameter {k}.'
                )
            params[k] = v
            keys.remove(k)

        for k in keys:
            if all_params[k] is None:
                raise ValueError(
                    f'Missing required configuration parameter {k}.'
                )
            params[k] = all_params[k]
        
        self._params = params

        if not self._is_valid():
            raise ValueError(
                f'Invalid configuration parameters. Check the documentation.'
            )

    # MARK: Instance Methods
    def save(self, file):
        """
        Saves the configuration to a JSON file.

        Parameters:
        -----------
        - file: str
            The full path to the file. The extension does not need to be
            specified, but must be .json.
        """
        ensure_valid_directories(file)
        if not file.endswith('.json'):
            file += '.json'
        with open(file, 'w+') as f:
            json.dump(self._params, f, indent=4, sort_keys=True)

    # MARK: Private Methods
    def _is_valid(self):
        """
        Checks whether the given configuration is valid. This method should be
        overridden if required. The default implementation implies validity.

        Returns:
        --------
        - bool
            Whether the configuration is valid.
        """
        return True

    # MARK: Special Methods
    def __repr__(self):
        return self._params.__repr__()

    def __getattr__(self, name):
        if name == '_params':
            raise AttributeError()
        try:
            return self._params[name]
        except KeyError:
            class_name = self.__class__.__name__
            raise AttributeError(
                f'Configuration {class_name} has no parameter {name}.'
            )


class Configurable(ABC):
    """
    Mixin class to make torch.nn.Module configurable in an easy and standardized
    way. For initialization, a module is then given a single config file of 
    type ``bxtorch.nn.Config``. Properties of the configuration can be easily 
    accessed via ``self.<property>``. Additionally, this class makes it easy
    to save and load the module in a consistent way.

    When subclassing a PyTorch module, make sure to include the Configurable
    mixin as *first* dependency.

    Note:
    -----
    Only top-level modules should use this mixin to profit from saving/loading
    modules easily.
    """

    # MARK: Static Methods
    @classmethod
    def load(cls, file):
        """
        Loads the model by loading a configuration defining the architecture
        and another file containing the weights for this architecture.

        Parameters:
        -----------
        - file: str
            The full path to the file. The configuration will be loaded from
            <file>.json and the model's weights will be loaded from <file>.pt.

        Returns:
        --------
        - bxtorch.nn.Configurable
            The loaded model.
        """
        if cls._config_class() is not None:
            config = cls._config_class().load(file)
            model = cls(config)
        else:
            model = cls(None)
        params = torch.load(f'{file}.pt')
        model.load_state_dict(params)
        return model

    @abstractclassmethod
    def _config_class(cls):
        """
        Defines the config class which the module uses for configuration.

        Returns:
        --------
        - type like bxtorch.nn.Config
            The configuration class.
        """
        pass

    # MARK: Initialization
    def __init__(self, config):
        super(Configurable, self).__init__()
        self._config = config

    # MARK: Computed Properties
    @property
    def num_parameters(self):
        return sum(p.numel() for p in self.parameters())

    @property
    def num_trainable_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    # MARK: Instance Methods
    def save(self, file):
        """
        Saves the model and its configuration to two files.

        Parameters:
        -----------
        - file: str
            The full path to the file. The configuration will be saved to
            <file>.json while the model's weights will be saved to <file>.pt.
        """
        ensure_valid_directories(file)
        self._config.save(file)
        # Ensure saving CPU model
        state_dict = copy.deepcopy(self.state_dict())
        result = {}
        for k, v in state_dict.items():
            result[k] = v.cpu()
        torch.save(result, f'{file}.pt')

    # MARK: Special Methods
    def __getattr__(self, name):
        try:
            return super(Configurable, self).__getattr__(name)
        except AttributeError:
            if name == '_config':
                raise AttributeError()
            return getattr(self._config, name)
