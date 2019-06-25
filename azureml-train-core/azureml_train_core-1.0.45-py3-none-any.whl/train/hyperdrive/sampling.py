# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The hyperparameter sampling definitions."""
import inspect
import sys
from abc import ABC

from azureml.exceptions import AzureMLException


def _sampling_from_dict(dict_sampling):
    """Construct a Sampling object from a dictionary.

    The dictionary is supposed to come from a previous run that's retrieved from the cloud.
    This is an internal utility method.

    :param dict_sampling: A dictionary of the sampling.
    :type dict_sampling: dict
    """
    if not isinstance(dict_sampling, dict):
        raise TypeError("Expecting type '{}', got '{}' for '{}'.".format(dict,
                                                                         type(dict_sampling),
                                                                         dict_sampling))
    if "name" not in dict_sampling:
        raise ValueError("Couldn't find '{}' entry.".format("name"))

    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    for cls in clsmembers:
        if not hasattr(cls[1], 'SAMPLING_NAME'):
            continue

        if cls[1].SAMPLING_NAME.lower() == dict_sampling["name"].lower():
            return cls[1]._from_dict(dict_sampling)

    raise ValueError("Unknown sampling '{}'".format(dict_sampling["name"]))


class HyperParameterSampling(ABC):
    """Abstract base class for all hyperparameter sampling algorithms.

    It encapsulates the hyperparameter space, the sampling method and additional properties.

    :param sampling_method_name: Name of the sampling method.
    :type sampling_method_name: str
    :param parameter_space: A dictionary containing each parameter and its distribution.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    :param supported_distributions: A list of the supported distribution methods. Default of None indicates all
            distributions are supported.
    :type supported_distributions: set[str]
    """

    def __init__(self, sampling_method_name, parameter_space, properties=None,
                 supported_distributions=None, distributions_validators=None):
        """Initialize HyperParameterSampling.

        :param sampling_method_name: Name of the sampling method.
        :type sampling_method_name: str
        :param parameter_space: A dictionary containing each parameter and its distribution.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        :param supported_distributions: A list of the supported distribution methods. Default of None indicates all
                distributions are supported.
        :type supported_distributions: set[str]
        :param distributions_validators: A dictionary that maps a distribution name to a function that validates
                if it is a valid distribution for the sampling method used. Default of None indicates that
                no particular validators are needed.
        :type distributions_validators: dict
        """
        self._sampling_method_name = sampling_method_name
        self._parameter_space = parameter_space
        self._properties = properties
        self._supported_distributions = supported_distributions
        self._distributions_validators = distributions_validators
        self._validate_supported_distributions()

    def to_json(self):
        """Return the json of the hyperparameter sampling object.

        :returns: JSON formatted sampling policy.
        :rtype: str
        """
        definition = \
            {
                "name": self._sampling_method_name,
                "parameter_space": self._parameter_space
            }
        if self._properties:
            definition["properties"] = self._properties

        return definition

    def _validate_supported_distributions(self):
        if self._supported_distributions:
            for distribution in self._parameter_space.values():
                if distribution[0] not in self._supported_distributions:
                    msg = "Distribution '{}' not supported. Only [{}] are supported for this sampling method." \
                        .format(distribution[0], ", ".join(self._supported_distributions))
                    raise AzureMLException(msg)
                if self._distributions_validators is not None and \
                        distribution[0] in self._distributions_validators:
                    validation_result = self._distributions_validators[distribution[0]](distribution)
                    if not validation_result[0]:
                        raise AzureMLException(validation_result[1])

    def __eq__(self, other):
        """Define equality in terms of the equality of the properties."""
        return self.__dict__ == other.__dict__

    @staticmethod
    def _validate_dict_sampling(dict_sampling, name):
        if not isinstance(dict_sampling, dict) or \
                "name" not in dict_sampling or \
                dict_sampling["name"].lower() != name.lower():
            raise ValueError("Invalid arguments '{}', '{}' for this method.".format(dict_sampling, name))

        if "parameter_space" not in dict_sampling:
            raise ValueError("Couldn't find 'parameter_space' entry.")


class RandomParameterSampling(HyperParameterSampling):
    """Random hyperparameter space sampling.

    In this sampling space, the parameter value can either be a choice among discrete values
    or distribution over a continuous range for each value,
    like for instance uniform, loguniform, normal, lognormal, etc.
    For example,

    .. code-block:: python

        {
            "init_lr": uniform(0.0005, 0.005),
            "hidden_size": choice(0, 100, 120, 140, 180)
        }

    This will define a search space with two parameters, init_lr and hidden_size.
    The init_lr can have a uniform distribution with 0.0005 as min and 0.005 as max value, and
    the hidden_size one of [80, 100, 120, 140, 180].

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    """

    SAMPLING_NAME = "RANDOM"

    def __init__(self, parameter_space, properties=None):
        """Initialize RandomParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        """
        super().__init__(RandomParameterSampling.SAMPLING_NAME, parameter_space, properties)

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling, RandomParameterSampling.SAMPLING_NAME)

        return RandomParameterSampling(parameter_space=dict_sampling["parameter_space"])


class GridParameterSampling(HyperParameterSampling):
    """Grid hyperparameter space sampling.

    In this sampling space, the parameter value is only a choice among the discrete values.
    For example,

    .. code-block:: python

        {
          "lr": choice(1, 2, 3),
          "batch": choice(8, 9)
        }

    This will define a search space with two parameters, lr and batch.
    The lr can have one of the values [1, 2, 3 ], and the batch one of [8, 9].

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter.
    :type parameter_space: dict
    """

    SAMPLING_NAME = "GRID"

    def __init__(self, parameter_space):
        """Initialize GridParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter.
        :type parameter_space: dict
        """
        supported_distributions = {'choice'}
        super().__init__(GridParameterSampling.SAMPLING_NAME,
                         parameter_space, supported_distributions=supported_distributions)

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling,
                                                       GridParameterSampling.SAMPLING_NAME)

        return GridParameterSampling(parameter_space=dict_sampling["parameter_space"])


class BayesianParameterSampling(HyperParameterSampling):
    """Bayesian hyperparameter space sampling.

    Bayesian sampling tries to intelligently pick the next sample of hyperparameters,
    based on how the previous samples performed, such that the new sample improves
    the reported primary metric.

    Please note that when using Bayesian, the number of concurrent runs has an impact
    on the effectiveness of the tuning process. Typically, a smaller number of concurrent
    runs can lead to better sampling convergence. That is because some runs start without
    fully benefiting from runs that are still running.

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter. Please note that only choice,
                            quniform and uniform are supported for Bayesian optimization.
    :type parameter_space: dict
    """

    SAMPLING_NAME = "BayesianOptimization"

    def __init__(self, parameter_space):
        """Initialize BayesianParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter. Please note that only choice,
                                quniform and uniform are supported for Bayesian optimization.
        :type parameter_space: dict
        """
        if parameter_space is None:
            raise AzureMLException("parameter_space cannot be None")

        supported_distributions = {'choice', 'quniform', 'uniform'}
        distributions_validators = {'choice': self._choice_validator}
        super().__init__(BayesianParameterSampling.SAMPLING_NAME, parameter_space,
                         supported_distributions=supported_distributions,
                         distributions_validators=distributions_validators)

    @staticmethod
    def _choice_validator(choice_definition):
        """Validate the choice distribution arguments.

        :param choice_definition: Distribution to validate.
        :return: a tuple <True, None> if the choice distribution is correctly defined, or <False, Message> if not.
        """
        choice_values = choice_definition[1][0]
        for value in choice_values:
            if not type(value) in (int, str, float):
                return False, "'choice' values should be 'int', 'string' or 'float'. Got '{}'.".format(type(value))

        return True, None

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling,
                                                       BayesianParameterSampling.SAMPLING_NAME)

        return BayesianParameterSampling(parameter_space=dict_sampling["parameter_space"])
