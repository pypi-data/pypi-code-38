from typing import List, Union, TypeVar, Callable, Any, Dict, Sequence

from sklearn.base import BaseEstimator

import mindfoundry.optaas.client.parameter as base
from mindfoundry.optaas.client.sklearn_pipelines.utils import _make_id

T = TypeVar('T', bound=base.Parameter)


class SklearnParameterMaker:
    """Creates :class:`Parameters <.Parameter>` with the correct names and default values for optimizing a sklearn :class:`.Pipeline`

    Convenience methods are provided for each :class:`.Parameter` subclass, so that you can call `sk.IntParameter(...)`
    instead of `IntParameter(...)`.
    """

    def __init__(self, estimator_id: str, estimator: BaseEstimator) -> None:
        self.prefix = estimator_id + '__'
        self.defaults: Dict[str, Any] = estimator.get_params()

    def GroupParameter(self, name: str, items: List[base.Parameter], optional: bool = None) -> base.GroupParameter:  # pylint: disable=invalid-name
        return self.make_parameter(base.GroupParameter, name=name, items=items, optional=optional)

    def ChoiceParameter(self, name: str, choices: List[base.Parameter], optional: bool = None) -> base.ChoiceParameter:  # pylint: disable=invalid-name
        return self.make_parameter(base.ChoiceParameter, name=name, choices=choices, optional=optional)

    def CategoricalParameter(self, name: str, values: Sequence[Union[str, int, float, bool]],  # pylint: disable=invalid-name
                             optional: bool = None) -> base.CategoricalParameter:
        return self.make_parameter(base.CategoricalParameter, name=name, values=values, optional=optional)

    def SubsetParameter(self, name: str, values: List[Union[str, int, float, bool]],  # pylint: disable=invalid-name
                        optional: bool = None) -> base.SubsetParameter:
        return self.make_parameter(base.SubsetParameter, name=name, values=values, optional=optional)

    def ConstantParameter(self, name: str, value: Union[str, int, float, bool],  # pylint: disable=invalid-name
                          optional: bool = None) -> base.ConstantParameter:
        return self.make_parameter(base.ConstantParameter, name=name, value=value, optional=optional, )

    def BoolParameter(self, name: str, optional: bool = None) -> base.BoolParameter:  # pylint: disable=invalid-name
        return self.make_parameter(base.BoolParameter, name=name, optional=optional)

    def IntParameter(self, name: str, minimum: int, maximum: int, distribution: base.Distribution = None,  # pylint: disable=invalid-name
                     optional: bool = None) -> base.IntParameter:
        return self.make_parameter(base.IntParameter, name=name, minimum=minimum, maximum=maximum, optional=optional,
                                   distribution=distribution)

    def FloatParameter(self, name: str, minimum: float, maximum: float, distribution: base.Distribution = None,  # pylint: disable=invalid-name
                       optional: bool = None) -> base.FloatParameter:
        return self.make_parameter(base.FloatParameter, name=name, minimum=minimum, maximum=maximum, optional=optional,
                                   distribution=distribution)

    def IntOrAuto(self, name: str, minimum: int, maximum: int, distribution: base.Distribution = None,  # pylint: disable=invalid-name
                  optional: bool = None) -> base.ChoiceParameter:
        """Creates a choice between an IntParameter and the string 'auto'."""
        return self.IntOrCategorical(name, minimum=minimum, maximum=maximum, categories=["auto"], optional=optional,
                                     distribution=distribution)

    def IntOrCategorical(self, name: str, minimum: int, maximum: int, categories: List[str],  # pylint: disable=invalid-name
                         distribution: base.Distribution = None, optional: bool = None) -> base.ChoiceParameter:
        """Creates a choice between an IntParameter and a CategoricalParameter."""
        return self.ChoiceParameter(name, choices=[
            self.IntParameter(name=name + '_int', minimum=minimum, maximum=maximum, optional=optional,
                              distribution=distribution),
            self.CategoricalParameter(name=name + '_cat', values=categories)
        ])

    def FloatOrAuto(self, name: str, minimum: float, maximum: float, distribution: base.Distribution = None,  # pylint: disable=invalid-name
                    optional: bool = None) -> base.ChoiceParameter:
        """Creates a choice between a FloatParameter and the string 'auto'."""
        return self.FloatOrCategorical(name, minimum=minimum, maximum=maximum, categories=["auto"], optional=optional,
                                       distribution=distribution)

    def FloatOrCategorical(self, name: str, minimum: float, maximum: float, categories: List[str],  # pylint: disable=invalid-name
                           distribution: base.Distribution = None, optional: bool = None) -> base.ChoiceParameter:
        """Creates a choice between a FloatParameter and a CategoricalParameter."""
        return self.ChoiceParameter(name, choices=[
            self.FloatParameter(name=name + '_float', minimum=minimum, maximum=maximum, optional=optional,
                                distribution=distribution),
            self.CategoricalParameter(name=name + '_cat', values=categories)
        ])

    def DictParameter(self, name: str, items: List[base.Parameter], optional: bool = None) -> base.GroupParameter:  # pylint: disable=invalid-name
        """Creates a parameter whose value will be passed into an estimator as a dict."""
        return self.GroupParameter(name, optional=optional, items=[
            self.GroupParameter(name + '_dict_', items=items)
        ])

    def make_parameter(self, parameter_type: Callable[..., T], name: str, **kwargs) -> T:
        """Creates a parameter so as to facilitate the generation of a sklearn Pipeline from a :class:`.Configuration`.

        Args:
            parameter_type (Callable[..., T]): The specific Parameter subclass of the parameter you want to create, e.g. :class:`.IntParameter`.
            name (str): Parameter name, should match the name expected by the estimator's `set_params` method exactly.
            kwargs: Any additional arguments for the parameter constructor, e.g. `minimum`, `maximum`, `choices` etc.
                **Do not** include a value for the `id` and `default` arguments, because it will be overwritten.
                The `id` will be generated from the parameter name (any spaces will be replaced by underscores) and prefixed
                with the estimator name.
                The `default` will be taken from `estimator.get_params()`, i.e. it should be set in the estimator constructor.
        """

        kwargs['name'] = name
        kwargs['id'] = _make_id(self.prefix + name)

        default = self.defaults.get(name)

        if default is None:
            kwargs.pop('default', None)
            if kwargs.get('optional') is True:
                kwargs['include_in_default'] = False
        else:
            if parameter_type == base.ChoiceParameter:
                default_choice = _get_default_choice(default, kwargs)
                if not isinstance(default_choice, base.ConstantParameter):
                    setattr(default_choice, 'default', default)
                if hasattr(default_choice, 'includeInDefault'):
                    delattr(default_choice, 'includeInDefault')
                default = default_choice
            elif parameter_type == base.GroupParameter:
                for i, value in enumerate(default):
                    item = kwargs['items'][i]
                    setattr(item, 'default', value)
                    if hasattr(item, 'includeInDefault'):
                        delattr(item, 'includeInDefault')

            kwargs.pop('include_in_default', None)

            if parameter_type != base.GroupParameter:
                kwargs['default'] = default

        return parameter_type(**kwargs)


def _get_default_choice(default_value, kwargs) -> base.Parameter:
    for choice in kwargs['choices']:
        if choice.is_compatible_value(default_value):
            return choice
    raise ValueError(f"{default_value} is not a valid default value for parameter '{kwargs['name']}'")
