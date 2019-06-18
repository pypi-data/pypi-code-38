import abc
from enum import Enum
from typing import List, Union, Any, Optional, Dict

from mindfoundry.optaas.client.constraint import ConstraintExpression, UnaryPredicate


class Parameter(ConstraintExpression, abc.ABC):
    """Superclass for all parameters.

    Attributes:
        name (str): Human-readable name for the parameter.
        type (str): Parameter type (e.g. "integer" or "choice")
        id (str, optional): Unique id for this Parameter. If not specified, the object id will be used.
        optional (bool, optional, default False): Whether the parameter can be omitted in a :class:`.Configuration`.
        include_in_default (bool, optional, default True): Whether an optional parameter will be included in the :attr:`default Configuration<.Configuration.type>`.
        default (Any, optional): Value to use when generating the :attr:`default Configuration<.Configuration.type>`.
    """

    def __init__(self, name: str, type_: str, id_: Optional[str],
                 optional: Optional[bool] = False, include_in_default: Optional[bool] = True, default=None) -> None:
        self.id = id_ or str(id(self))  # pylint: disable=invalid-name
        self.name = name
        self.type = type_
        if optional:
            self.optional = True
        if default is not None:
            self.default = default
        if include_in_default is not None:
            self.includeInDefault = include_in_default  # pylint: disable=invalid-name

    @abc.abstractmethod
    def is_compatible_value(self, value: Any) -> bool:
        """Returns True iff the given value is compatible with this Parameter."""
        pass

    def is_present(self) -> ConstraintExpression:
        """Returns a :class:`.ConstraintExpression` that evaluates to True if this parameter is present in a :class:`.Configuration`"""
        return UnaryPredicate(self, 'is_present')

    def is_absent(self) -> ConstraintExpression:
        """Returns a :class:`.ConstraintExpression` that evaluates to False if this parameter is present in a :class:`.Configuration`"""
        return UnaryPredicate(self, 'is_absent')

    def to_json(self) -> Dict:
        """JSON representation of this Parameter (used when making a request to OPTaaS to create the :class:`.Task`)"""
        return vars(self)

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return self.name

    def to_optaas_expression(self) -> str:
        return '#' + self.id


class GroupParameter(Parameter):
    """A set of Parameters, all of which will be included in each :class:`.Configuration` unless marked as :attr:`.Parameter.optional`.

    There is no `default` value for groups.

    Attributes:
        items (List[Parameter]): Parameters that comprise this Group. Can be empty.
    """

    def __init__(self, name: str, items: List[Parameter], id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None) -> None:
        super().__init__(name, 'group', id, optional, include_in_default)
        self.items = items

    def to_json(self) -> dict:
        json = super().to_json().copy()
        json['items'] = [p.to_json() for p in self.items]
        return json

    def is_compatible_value(self, value: Any) -> bool:
        """Always False because GroupParameter never stores a single value."""
        return False


class ChoiceParameter(Parameter):
    """A set of Parameters, only one of which will be chosen to appear in each :class:`.Configuration`.

    Attributes:
        choices (List[Parameter]): Parameters to choose from. Cannot be empty.
        default (Parameter, optional): Default choice, must be present in the `choices` list.
            If not specified, the default will be the first item in `choices`.

    Raises:
        :class:`.ValueError` if `default` is not present in `choices`.
    """

    def __init__(self, name: str, choices: List[Parameter], id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None, default: Parameter = None) -> None:
        if default is None:
            default_id = None
        else:
            if not any(choice for choice in choices if choice is default):
                raise ValueError(f"Default '{default}' is not one of the choices in ChoiceParameter '{name}'")
            default_id = f'#{default.id}'

        super().__init__(name, 'choice', id, optional, include_in_default, default_id)
        self.choices = choices

    def to_json(self) -> dict:
        json = super().to_json().copy()
        json['choices'] = [c.to_json() for c in self.choices]
        return json

    def is_compatible_value(self, value: Any) -> bool:
        """Always False because ChoiceParameter never stores a single value."""
        return False


class CategoricalParameter(Parameter):
    """A Parameter which can be assigned any value from a specified list of allowed values.

    Args:
        values (List[Union[str, int, float, bool]]): Allowed values (can be string, numeric, boolean or any mixture of those).
        default (Union[str, int, float, bool], optional):
            If defined, must be equal to a value from `values`.
            If not defined, the default will be the first value from `values`.
    """

    def __init__(self, name: str, values: List[Union[str, int, float, bool]],
                 id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None, default=None) -> None:
        if default is not None and default not in values:
            raise ValueError(f"Default '{default}' is not one of the values in CategoricalParameter '{name}'")
        super().__init__(name, 'categorical', id, optional, include_in_default, default)
        self.enum = values

    def is_compatible_value(self, value: Any) -> bool:
        """Value must be identical to one of the specified values."""
        for allowed_value in self.enum:
            if value == allowed_value and type(value) == type(allowed_value):
                return True
        return False


class SubsetParameter(Parameter):
    """A parameter that may contain any subset of a valid set of values.

    Args:
        values (List[Union[str, int, float, bool]])
            Allowed values (can be string, numeric, boolean or any mixture of those).
        default (List[Union[str, int, float, bool]])
            The default for this kind of parameter must be a subset of allowed values. Optional. Assumed to be the empty
            set if not otherwise specified.

    """

    def __init__(self, name: str, values: List[Union[str, int, float, bool]],
                 id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None,
                 default: List[Union[str, int, float, bool]] = None) -> None:
        super().__init__(name, 'subset', id, optional, include_in_default, default)
        self.allowedValues = values  # pylint: disable=invalid-name

        if not values:
            raise ValueError(f"The empty list is not a valid set of values for SubsetParameter '{name}'")

        if None in values:
            raise ValueError(f"'None' is not a valid value for SubsetParameter '{name}'")

        if (default is not None) and (not self.is_compatible_value(default)):
            raise ValueError(f"Default '{default}' is not a subset of the values in SubsetParameter '{name}'")

    def is_compatible_value(self, value: List[Any]) -> bool:
        """
        Value must be a subset of allowed values, i.e. all of its element must be included in the set of
        allowed values. An empty subset is also a valid value by extension. No duplicate items are allowed.
        """
        if value is None:
            return False

        value_set = set(value)

        # Fails if either any item is not a value of enum or if item was seen more than once
        return (value_set <= set(self.allowedValues)) and (len(value) == len(value_set))


class ConstantParameter(Parameter):
    """A Parameter which will always be assigned a specified value.

    Args:
        value (Union[str, int, float, bool]): value (can be string, numeric or boolean).
    """

    def __init__(self, name: str, value: Union[str, int, float, bool],
                 id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None) -> None:
        super().__init__(name, 'constant', id, optional, include_in_default)
        self.value = value

    def is_compatible_value(self, value: Any) -> bool:
        """Value must be identical to the specified value."""
        return value == self.value and type(value) == type(self.value)


class BoolParameter(Parameter):
    """A Parameter which will be assigned either True or False.

    Args:
        default (bool, optional): False if not specified.
    """

    def __init__(self, name: str, id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None, default: bool = None) -> None:
        if default is not None and not isinstance(default, bool):
            raise ValueError(f"Default '{default}' is not a boolean in BoolParameter '{name}'")
        super().__init__(name, 'boolean', id, optional, include_in_default, default)

    def is_compatible_value(self, value: Any) -> bool:
        """Value must be a bool."""
        return isinstance(value, bool)


class Distribution(Enum):
    """Specifies the distribution of values for a NumericParameter.

    This will influence the values assigned by OPTaaS in each :class:`.Configuration`.
    """
    UNIFORM = "Uniform"
    LOGUNIFORM = "LogUniform"


class NumericParameter(Parameter, abc.ABC):
    """Superclass for FloatParameter and IntParameter"""

    def __init__(self, name: str, type_: str, minimum: Union[int, float], maximum: Union[int, float],
                 id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None,
                 default: Union[int, float] = None, distribution: Distribution = None) -> None:
        super().__init__(name, type_, id, optional, include_in_default, default)
        self.minimum = minimum
        self.maximum = maximum
        if distribution is not None:
            self.distribution = distribution.value

    @abc.abstractmethod
    def is_compatible_value(self, value: Any) -> bool:
        pass


class IntParameter(NumericParameter):
    """A Parameter which can be assigned any integer value between the `minimum` and `maximum` (inclusive).

    Args:
        minimum (int): Smallest allowed value.
        maximum (int): Largest allowed value.
        default (int, optional):
            If defined, must be a value between `minimum` and `maximum`.
            If not defined, it will be set to the midpoint between `minimum` and `maximum`.
        distribution (Distribution, optional, default Distribution.UNIFORM): See :class:`.Distribution`
    """

    def __init__(self, name: str, minimum: int, maximum: int, id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None,
                 default: int = None, distribution: Distribution = None) -> None:
        if default is not None and not isinstance(default, int):
            raise ValueError(f"Default '{default}' is not an integer in IntParameter '{name}'")

        super().__init__(name, 'integer', minimum, maximum, id, optional, include_in_default, default, distribution)

    def is_compatible_value(self, value: Any) -> bool:
        """Value must be an int (not bool) and within the range [minimum - maximum] (inclusive)."""
        return isinstance(value, int) and not isinstance(value, bool) and self.minimum <= value <= self.maximum


class FloatParameter(NumericParameter):
    """A Parameter which can be assigned any float value between the `minimum` and `maximum` (inclusive).

    Args:
        minimum (float): Smallest allowed value.
        maximum (float): Largest allowed value.
        default (float, optional):
            If defined, must be a value between `minimum` and `maximum`.
            If not defined, it will be set to the midpoint between `minimum` and `maximum`.
        distribution (Distribution, optional, default Distribution.UNIFORM): See :class:`.Distribution`
        cyclical (bool, optional, default False):
            If True, OPTaaS will select values from a period starting at the `minimum` (inclusive) and ending at the `maximum`
            (exclusive). Values near the minimum and maximum will be considered to be close, as if they were on a circle.
            **Note:** if `cyclical` is true, `distribution` will be ignored. Also, if any of your parameters are cyclical, all
            your parameters must be Floats, Constants or Groups (other types are not currently supported), and none of them can
            be `optional`.
    """

    def __init__(self, name: str, minimum: float, maximum: float, id: str = None,  # pylint: disable=redefined-builtin
                 optional: bool = None, include_in_default: bool = None, default: float = None,
                 distribution: Distribution = None, cyclical: bool = None) -> None:
        if default is not None and not isinstance(default, float) and not isinstance(default, int):
            raise ValueError(f"Default '{default}' is not a float in FloatParameter '{name}'")

        super().__init__(name, 'number', minimum, maximum, id, optional, include_in_default, default, distribution)
        if cyclical is not None:
            self.cyclical = cyclical

    def is_compatible_value(self, value: Any) -> bool:
        """Value must be a float or int (not bool) and within the range [minimum - maximum] (inclusive)."""
        return isinstance(value, (float, int)) and not isinstance(value, bool) and self.minimum <= value <= self.maximum
