import abc
import inspect
import itertools
import json
import reprlib
from typing import Any, List, Tuple

from .factory import OperatorFactory


class Serializable(abc.ABC):

    op_factory = OperatorFactory()

    @classmethod
    def __init_subclass__(cls):
        if cls.is_abstract():
            return

        cls.op_factory.register(cls.__name__, cls)

        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            argspec = inspect.getfullargspec(original_init)
            self._configs = {
                arg_name: val
                for arg_name, val in zip(
                    argspec.args[1:],  # omit `self`
                    args,
                )
            }
            self._configs.update(kwargs)
            if argspec.defaults:
                self._configs.update({
                    arg_name: default_val
                    for arg_name, default_val in zip(
                        reversed(argspec.args),
                        reversed(argspec.defaults),
                    )
                    if arg_name not in self._configs
                })

        cls.__init__ = __init__

    @classmethod
    def is_abstract(cls):
        return getattr(cls, '__abstractmethods__', None) is not None

    @classmethod
    def deserialize(cls, serialized_str: str):
        params = json.loads(serialized_str)
        return cls.from_dict(params)

    @classmethod
    def from_dict(cls, params):
        cls_name = params['op_name']
        kwargs = params['op_kwargs']
        return cls.op_factory[cls_name](**kwargs)

    def serialize(self) -> str:
        return json.dumps(
            {
                'op_name': self.__class__.__name__,
                'op_kwargs': self.configs,
            },
            ensure_ascii=False,
            indent=2,
        )

    @property
    def configs(self):
        return self._configs


class Operator(Serializable):

    """Base class for Operators

    Sub-classes should implement `_transform`

    Attributes:
        input_type: input type of sequence to transform
        output_type: output type of transformed sequence

    """

    _input_type = None
    _output_type = None

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.is_abstract():
            return

        cls.assert_has_class_attributes('_input_type', '_output_type')

    @classmethod
    def assert_has_class_attributes(cls, *attrs):
        for attr_name in attrs:
            assert getattr(cls, attr_name, None) is not None, \
                f"Concrete class: {cls} should declare `{attr_name}`!"

    @property
    def input_type(self):
        return self._input_type

    @property
    def output_type(self):
        return self._output_type

    def transform(self, input_sequence) -> Tuple[Any, 'LabelAligner']:
        """Transform input_sequence

        Transform input_sequence to certain form which meets the output_type
        and updates labels if necessary.

        Args:
            input_sequence (input_type): utterance or tokens

        Returns:
            output_sequence (output_type): the transformed result
            label_aligner (obj): an instance of LabelAligner

        Raises:
            TypeError: If input_type or output_type isn't correct.
        """

        if not isinstance(input_sequence, self.input_type):
            raise TypeError('Invalid input type')

        output_sequence, label_aligner = self._transform(input_sequence)
        if not isinstance(output_sequence, self.output_type):
            raise TypeError('Invalid output type')
        return output_sequence, label_aligner

    @abc.abstractmethod
    def _transform(self, input_sequence) -> Tuple[Any, 'LabelAligner']:
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self.configs == other.configs

    def __str__(self):

        def custom_repr(x, maxdict: int = 2):
            if isinstance(x, dict):  # NOTE: since reprlib.repr(dict) ignores the order
                body = ', '.join([
                    f"{key!r}: {val!r}"
                    for key, val in itertools.islice(x.items(), maxdict)
                ])
                return f"{{{body}, ...}}"
            return reprlib.repr(x)

        config_str = ', '.join([
            f"{key}={custom_repr(val)}"
            for key, val in self.configs.items()
        ])
        return f"{self.__class__.__name__}({config_str})"


class LabelAligner(abc.ABC):

    """Base class for LabelAligners

    Sub-classes should implement `_transform` and `_inverse_transform`

    Attributes:
        input_sequence: utterance or tokens
        output_length (int): the length of transformed sequence
        edit: process of transformation documented by `edit` structure

    """

    def __init__(self, input_sequence, edit, output_length: int):
        self._input_length = len(input_sequence)
        self._output_length = output_length

        self._input_sequence = input_sequence
        self._forward_edit = edit

    def transform(self, labels: List[int]) -> List[int]:
        """Update labels according to forward edit

        Args:
            labels (ints): has same length as the input_sequence of Operator.transfrom

        Raise:
            ValueError if length of labels is not matched.

        Return:
            labels (ints): has same length as the output_sequence of Operator.transform

        """
        self._validate_input(labels)
        output_labels = self._transform(labels)
        self._validate_output(output_labels)
        return output_labels

    def inverse_transform(self, labels: List[int]) -> List[int]:
        """Realign model predictions to original input

        Args:
            labels (ints): has same length as the output_sequence of Operator.transfrom

        Raise:
            ValueError if length of labels is not matched.

        Return:
            labels (ints): has same length as the input_sequence of Operator.transform

        """
        self._validate_output(labels)
        output_labels = self._inverse_transform(labels)
        self._validate_input(output_labels)
        return output_labels

    def _validate_input(self, labels: List[int]):
        if len(labels) != self._input_length:
            raise ValueError('Invalid input labels')

    def _validate_output(self, labels: List[int]):
        if len(labels) != self._output_length:
            raise ValueError('Invalid output labels')

    @abc.abstractmethod
    def _transform(self, labels: List[int]) -> List[int]:
        pass

    @abc.abstractmethod
    def _inverse_transform(self, labels: List[int]) -> List[int]:
        pass


class NullLabelAligner(LabelAligner):

    def _transform(self, labels: List[int]):
        return labels

    def _inverse_transform(self, labels):
        return labels
