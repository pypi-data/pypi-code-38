from abc import abstractmethod
import re
from typing import Optional, Sequence

import sympy

from .samples import SampleIndex
from .. import exceptions
from ..helpers import log


class CardinalitySpec:
    def __init__(self, parent):
        self.parent = parent

    @abstractmethod
    def __str__(self) -> str:
        """
        String version of the cardinality spec, should be parseable by
        create_cardinality
        """

    def __repr__(self) -> str:
        """
        Console representation of the cardinality spec
        """
        return '<{} {}>'.format(type(self).__name__, self)

    @abstractmethod
    def __eq__(self, other):
        """Test for equality"""

    def __ne__(self, other):
        return not self == other

    @property
    def predefined(self):
        """
        Indicate whether the cardinality is predefined or can only be calculated
        after execution
        """
        return False

    def validate(self, payload: Optional[dict], cardinality: int, planning=True) -> bool:
        """
        Validate cardinality given a payload and cardinality

        :param payload: Payload of the corresponding job
        :param cardinality: Cardinality to validate
        :return: Validity of the cardinality given the spec and payload
        """
        if isinstance(cardinality, (sympy.Symbol, sympy.Expr)):
            return planning

        result = self._validate(payload, cardinality)
        if isinstance(result, bool):
            return result
        elif isinstance(result, (sympy.Symbol, sympy.Expr)):
            return True
        else:
            raise exceptions.FastrTypeError(
                'Cardinality validation should be either a sympy expression'
                ' or boolean, found a {}'.format(type(result).__name__)
            )

    @abstractmethod
    def _validate(self, payload: Optional[dict], cardinality: int) -> bool:
        """
        Validate cardinality given a payload and cardinality

        :param payload: Payload of the corresponding job
        :param cardinality: Cardinality to validate
        :return: Validity of the cardinality given the spec and payload
        """

    def calculate_planning_cardinality(self) -> Optional[int]:
        """
        Calculate the cardinality given the node and spec, for cardinalities
        that only have validation and not a pre-calculable value, this return
        None.

        :param node: Node for which the cardinality is calculated
        :return: calculated cardinality
        """
        return None

    def calculate_execution_cardinality(self, key=None) -> Optional[int]:
        """
        Calculate the cardinality given the node and spec, during execution
        this should be available and not give unknowns once the data is present
        and the key is given.

        :param key: Key for which the cardinality is calculated
        :return: calculated cardinality
        """
        if key is None:
            return None

        sample = self.parent.samples.get(key)

        if sample is None:
            return None

        return sample.cardinality

    def calculate_job_cardinality(self, payload: dict) -> Optional[int]:
        """
        Calculate the actually cardinality when a job needs to know how many
        arguments to create for a non-automatic output.
        """
        return None


class IntCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, value: int):
        super().__init__(parent)
        self.value = value

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return self.value == other.value

    def __str__(self) -> str:
        return '{}'.format(self.value)

    def calculate_job_cardinality(self, payload: dict) -> Optional[int]:
        return self.value

    @property
    def predefined(self):
        return True

    def _validate(self, payload: dict, cardinality: int) -> bool:
        return self.value == cardinality

    def calculate_planning_cardinality(self) -> int:
        return self.value

    def calculate_execution_cardinality(self, node) -> int:
        return self.value


class MinCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, value: int):
        super().__init__(parent)
        self.value = value

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return self.value == other.value

    def __str__(self) -> str:
        return '{}-*'.format(self.value)

    def _validate(self, payload: dict, cardinality: int) -> bool:
        return cardinality >= self.value


class MaxCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, value: int):
        super().__init__(parent)
        self.value = value

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return self.value == other.value

    def __str__(self) -> str:
        return '*-{}'.format(self.value)

    def _validate(self, payload: dict, cardinality: int) -> bool:
        return cardinality <= self.value


class RangeCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, min: int, max: int):
        super().__init__(parent)
        self.min = min
        self.max = max

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return self.min == other.min and self.max == other.max

    def __str__(self) -> str:
        return '{}-{}'.format(self.min, self.max)

    def _validate(self, payload: dict, cardinality: int) -> bool:
        return self.min <= cardinality <= self.max


class ChoiceCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, options: Sequence[int]):
        super().__init__(parent)
        self.options = tuple(options)

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return self.options == other.options

    def __str__(self) -> str:
        return '[{}]'.format(','.join(self.options))

    def _validate(self, payload: dict, cardinality: int) -> bool:
        return cardinality in self.options


class AnyCardinalitySpec(CardinalitySpec):
    def validate(self, payload: dict, cardinality: int) -> bool:
        return True

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented
        return True

    def __str__(self) -> str:
        return 'any'


class AsCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.target = target

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented

        return self.target == other.target

    def __str__(self) -> str:
        return 'as:{}'.format(self.target)

    @property
    def predefined(self):
        return True

    @property
    def node(self):
        return self.parent.node

    def _validate(self, payload: dict, cardinality: int) -> bool:
        if payload is None:
            return True

        value = payload['inputs'].get(self.target)
        if value is None:
            value = payload['outputs'].get(self.target, [])

        return cardinality == len(value)

    def calculate_planning_cardinality(self) -> Optional[int]:
        # Get cardinality from target if possible
        target = self.node.inputs.get(self.target)
        if target is not None:
            return target.cardinality()
        else:
            raise exceptions.FastrCardinalityError(
                'Cardinality references to invalid field '
                '({} is not an Input in this Node)'.format(self.target)
            )

    def calculate_execution_cardinality(self, key=None) -> Optional[int]:
        target = self.node.inputs.get(self.target)
        if target is None:
            raise exceptions.FastrCardinalityError('Cardinality references to invalid field '
                                                   '({} is not an Input in this Node)'.format(self.target))

        if key is None:
            # No key is used, call target without key
            cardinality = target.cardinality(None)
        elif all(x == 0 for x in target.size):
            # Target is empty, cardinality can be set to 0
            cardinality = 0
        elif target.size == (1,):
            # Target has only sample, it will be repeated, use first sample
            cardinality = target.cardinality((0,))
        elif len(self.node.input_groups) == 1:
            # The InputGroups are not mixed, we can request the key
            if len(key) == len(target.size):
                cardinality = target.cardinality(key)
            else:
                index_map = dict(zip(self.parent.dimnames, key))
                lookup = {v: dimname for dimname in self.parent.dimnames for value in self.node.parent.nodegroups.values() if dimname in value for v in value}
                lookup.update({x: x for x in self.parent.dimnames})
                if all(x in lookup for x in target.dimnames):
                    # Print there is broadcasting going on, we need to undo that here
                    matched_dimnames = [lookup[x] for x in target.dimnames]
                    matched_index = SampleIndex(index_map[x] for x in matched_dimnames)
                    cardinality = target.cardinality(matched_index)
                else:
                    raise exceptions.FastrSizeMismatchError(
                        'InputGroup has inconsistent size/dimension info for Input '
                        '{}, cannot figure out broadcasting used!'.format(target.fullid)
                    )
        else:
            log.debug('Unmixing key "{}" for cardinality retrieval'.format(key))
            # The InputGroups are mixed, find the part of the ID relevant to this Input
            test = self.node.input_group_combiner.unmerge(key)
            index = test[target.input_group]

            if len(index) == len(target.size):
                cardinality = target.cardinality(index)
            else:
                raise exceptions.FastrSizeMismatchError('TODO: add broadcasting to this branch?')

        return cardinality

    def calculate_job_cardinality(self, payload: dict) -> Optional[int]:
        target = payload['inputs'].get(self.target)

        if target is None:
            raise exceptions.FastrCardinalityError(
                'Cardinality references to invalid field '
                '({} is not an Input in this Node)'.format(self.target)
            )

        return len(target)


class ValueCardinalitySpec(CardinalitySpec):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.target = target

    def __eq__(self, other):
        """Test for equality"""
        if type(self) != type(other):
            return NotImplemented

        return self.target == other.target

    def __str__(self) -> str:
        return 'val:{}'.format(self.target)

    @property
    def node(self):
        return self.parent.node

    def _validate(self, payload: dict, cardinality: int) -> bool:
        if payload is None:
            return True

        value = payload['inputs'].get(self.target)
        if value is None:
            value = payload['outputs'].get(self.target)

        if value is None:
            raise exceptions.FastrValueError('Cannot calculate val: type cardinality if value not in payload!')

        if len(value) != 1:
            return False

        try:
            value = int(value[0].value)
        except (ValueError, TypeError):
            return False

        return cardinality == value

    def calculate_execution_cardinality(self, key=None) -> Optional[int]:
        if self.target in self.node.inputs:
            # We cannot access to the jobs inputs it appears, so we
            # check if the output has already been generated.
            if self.parent.samples is not None and key in self.parent.samples:
                value = self.parent.samples[key].data
                log.debug('Got val via output data result, got {}'.format(value))
                return len(value)
            else:
                log.debug('Cannot get val: cardinality if there is no execution data!')
                return None
        elif self.target in self.node.outputs:
            # Get the value an output
            if key is None:
                return None

            output = self.node.outputs[self.target]

            if output.samples is None:
                return None

            # Try to cast via str to int (To make sure Int datatypes fares well)
            try:
                return int(str(output[key]))
            except exceptions.FastrKeyError:
                return None

    def calculate_job_cardinality(self, payload: dict) -> Optional[int]:
        target = payload['inputs'].get(self.target)

        if target is None:
            raise exceptions.FastrCardinalityError(
                'Cardinality references to invalid field '
                '({} is not an Input in this Node)'.format(self.target)
            )

        if len(target) != 1:
            raise exceptions.FastrValueError(
                'Cannot determine cardinality from multiple values '
                '(requested {}, found  {} as value)'.format(self, target)
            )

        return int(str(target[0]))


def create_cardinality(desc: str, parent) -> CardinalitySpec:
    """
    Create simplified description of the cardinality. This changes the
    string representation to a tuple that is easier to check at a later
    time.

    :param desc: the string version of the cardinality
    :parent: the parent input or output to which this cardinality spec belongs
    :return: the simplified cardinality description
    :raises FastrCardinalityError: if the Input/Output has an incorrect
            cardinality description.

    The translation works with the following table:

    ==================== ============================= ===============================================================
    cardinality string   cardinality spec              description
    ==================== ============================= ===============================================================
    ``"*"``, ``any``     ``('any',)                    Any cardinality is allowed
    ``"N"``              ``('int', N)``                A cardinality of N is required
    ``"N-M"``            ``('range', N, M)``           A cardinality between N and M is required
    ``"*-M"``            ``('max', M)``                A cardinality of maximal M is required
    ``"N-*"``            ``('min', N)``                A cardinality of minimal N is required
    ``"[M,N,...,O,P]"``  ``('choice', [M,N,...,O,P])`` The cardinality should one of the given options
    ``"as:input_id"``    ``('as', 'input_id')``        The cardinality should match the cardinality of the given Input
    ``"val:input_id"``   ``('val', 'input_id')``       The cardinliaty should match the value of the given Input
    ==================== ============================= ===============================================================

    .. note::

        The maximumu, minimum and range are inclusive

    """

    if isinstance(desc, int) or re.match(r'^\d+$', desc) is not None:
        # N
        return IntCardinalitySpec(parent, int(desc))
    elif desc in ['*', 'any', 'unknown']:
        # * (anything is okay)
        return AnyCardinalitySpec(parent)
    elif re.match(r'^\[\d+(,\d+)*\]', desc) is not None:
        # [M,N,..,O,P]
        return ChoiceCardinalitySpec(parent, [int(x) for x in desc[1:-1].split(',')])
    elif '-' in desc:
        match = re.match(r'^(\d+|\*)-(\d+|\*)$', desc)
        if match is None:
            raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")

        lower, upper = match.groups()

        if lower == '*' and upper == '*':
            # *-* (anything is okay)
            return AnyCardinalitySpec(parent)
        elif lower == '*' and upper != '*':
            # N-*
            return MaxCardinalitySpec(parent, int(upper))
        elif lower != '*' and upper == '*':
            # *-M
            return MinCardinalitySpec(parent, int(lower))
        else:
            # N-M
            return RangeCardinalitySpec(parent, int(lower), int(upper))

    elif desc.startswith("as:"):
        # as:other
        return AsCardinalitySpec(parent, desc[3:])
    elif desc.startswith("val:"):
        # val:other
        return ValueCardinalitySpec(parent, desc[4:])
    else:
        raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")
