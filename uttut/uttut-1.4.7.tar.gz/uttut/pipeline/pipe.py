from typing import Dict, List
import warnings

import json

from uttut.elements import Datum

from .intermediate import Intermediate
from .ops.base import LabelAligner, Operator
from .utils import unpack_datum


class Pipe:

    """Pipe is a container for a series of operators.

    Properties:
        steps: a list of operator instances.
        checkpoints: a mapping of checkpoints to index of steps.
        output_type: type of transformed output.
    """

    def __init__(self):
        self._steps: List[Operator] = []
        self._checkpoints: Dict[str, int] = {}

    def add(self, op_name: str, op_kwargs: Dict = None, checkpoint: str = None):
        """Add op into steps based on the operation name & kwargs.

        This method creates an operator given name & kwargs, and then append it
        to steps.

        Warning: This method will be deprecated, please use `add_op`.

        Args:
            op_name (str): the class name of operator.
            op_kwargs (dict): the keyword arguments to create operator.
            checkpoint (str): the name of checkpoint.

        Raises:
            TypeError: If input_type of op isn't consistent with pipe's output_type.
            KeyError: If the checkpoint name has already been added.
        """

        warnings.warn("This method will be deprecated, please use `add_op`.", DeprecationWarning)
        if op_kwargs is None:
            op_kwargs = {}

        op = Operator.from_dict({'op_name': op_name, 'op_kwargs': op_kwargs})
        self.add_op(op, checkpoint=checkpoint)

    def add_op(self, op: Operator, checkpoint: str = None):
        """Add op into steps

        Append the input op to steps.

        Args:
            op (Operator): An operator instance to be added to steps.
            checkpoint (str): the name of checkpoint

        Raises:
            TypeError: If input_type of operator isn't consistent with pipe's output_type.
            KeyError: If the checkpoint name has already been added.
        """

        if self.steps:
            if op.input_type != self.output_type:
                raise TypeError(
                    "InputType of the step op is not valid."
                    f"Got {op.input_type}, but requires {self.output_type}",
                )
        self._steps.append(op)

        if checkpoint is not None:
            if checkpoint in self.checkpoints:
                raise KeyError(f"duplicated checkpoints: {checkpoint}")
            self._checkpoints[checkpoint] = len(self.steps)

    def __eq__(self, other):
        return (self.steps, self.checkpoints) == (other.steps, other.checkpoints)

    def __add__(self, other):
        concat_pipe = self.__copy__()
        concat_pipe += other
        return concat_pipe

    def __iadd__(self, other):
        if self.output_type != other.input_type:
            raise TypeError(
                "input/output type of two pipes are not valid. "
                f"{self.output_type} != {other.input_type}",
            )
        if self.checkpoints.keys() & other.checkpoints.keys():
            raise KeyError(
                f"duplicated checkpoints between: {self.checkpoints}, {other.checkpoints}",
            )
        self._steps += other.steps
        self.checkpoints.update({
            ckpt_name: i + len(self.steps)  # since it's concated after self
            for ckpt_name, i in other.checkpoints.items()
        })
        return self

    def __copy__(self):
        copy_pipe = Pipe()
        copy_pipe._steps = self.steps.copy()
        copy_pipe._checkpoints = self.checkpoints.copy()
        return copy_pipe

    def __getitem__(self, key):
        if isinstance(key, slice):
            sub_pipe = Pipe()
            sub_pipe._steps = self.steps[key]
            sub_pipe._checkpoints = {
                ckpt_name: i - key.start
                for ckpt_name, i in self.checkpoints.items() if i > key.start
            }
            return sub_pipe

        return self.steps[key]

    def __len__(self):
        return len(self.steps)

    @property
    def steps(self) -> List[Operator]:
        return self._steps

    @property
    def checkpoints(self) -> Dict[str, int]:
        return self._checkpoints

    @property
    def input_type(self):
        if not self.steps:
            raise IndexError("Pipe is empty!")
        return self.steps[0].input_type

    @property
    def output_type(self):
        if not self.steps:
            raise IndexError("Pipe is empty!")
        return self.steps[-1].output_type

    def summary(self):
        print("_" * 80)
        print("Type  Operator")
        print("=" * 80)

        if self.steps:
            inverse_checkpoint = {
                idx: ckpt_name
                for ckpt_name, idx in self.checkpoints.items()
            }
            prev_type = self.input_type
            print(prev_type.__name__)
            print(" v")
            for idx, step in enumerate(self.steps, 1):
                print(" |   ", step)
                cur_type = step.output_type
                if cur_type != prev_type:
                    print(" v")
                    print(cur_type.__name__)
                    print(" v")
                prev_type = cur_type
                if idx in inverse_checkpoint:
                    print(" |")
                    print(f" @--> checkpoint: {inverse_checkpoint[idx]!r}")
                    print(" |")
            print(' v')
            print("=" * 80)
            print(f"{self.input_type.__name__} -> {self.output_type.__name__}")

        print(f"Total operators: {len(self.steps)}")
        print(f"Total checkpoints: {len(self.checkpoints)}")
        print("_" * 80)

    def transform(self, datum: Datum):
        """Process data based on steps

        This method processes datum according to the Pipe's steps.

        Arg:
            datum (Datum)

        Returns:
            output_sequence: transfromed sequence
            intent_labels (ints)
            entity_labels (ints)
            label_alingers: an instance of LabelAlignerSequence
            intermediate: an instance of Intermediate

        """
        input_sequence, intent_labels, entity_labels = unpack_datum(datum)
        output_sequence, label_aligners, intermediate = self.transform_sequence(input_sequence)
        updated_entity_labels = label_aligners.transform(entity_labels)

        return output_sequence, intent_labels, updated_entity_labels, label_aligners, intermediate

    def transform_sequence(self, input_sequence):
        """Process input_sequence based on steps

        This method processes input_sequence according to the Pipe's steps.

        Arg:
            input_sequence

        Returns:
            output_sequence: transfromed sequence
            label_alingers: an instance of LabelAlignerSequence
            intermediate: an instance of Intermediate

        """
        intermediate = Intermediate(self.checkpoints)

        intermediate.add(input_sequence)
        label_aligners = LabelAlignerSequence()

        for op in self.steps:
            input_sequence, label_aligner = op.transform(input_sequence)
            intermediate.add(input_sequence)
            label_aligners.add(label_aligner)

        return input_sequence, label_aligners, intermediate

    def serialize(self) -> str:
        return json.dumps(
            {
                'steps': [op.serialize() for op in self.steps],
                'checkpoints': self.checkpoints,
            },
            ensure_ascii=False,
            indent=2,
        )

    @classmethod
    def deserialize(cls, serialized_str: str) -> 'Pipe':
        pipe = cls()
        pipe_bundle = json.loads(serialized_str)
        # restore steps
        for step_info in pipe_bundle['steps']:
            if isinstance(step_info, str):
                op = Operator.deserialize(step_info)
            # backward compatibility
            elif isinstance(step_info, dict):
                op = Operator.from_dict(step_info)
            else:
                raise TypeError("Invalid json string format!")
            pipe.add_op(op)

        # restore checkpoints
        pipe._checkpoints = pipe_bundle['checkpoints']
        return pipe


class LabelAlignerSequence:

    def __init__(self):
        self.collections = []

    def add(self, label_aligner: LabelAligner):
        """Append label_aligner into collections

        Arg:
            label_aligner: an instance of LabelAligner

        """
        self.collections.append(label_aligner)

    def transform(self, labels: List[int]) -> List[int]:
        """Update labels based on given label_aligners

        Arg:
            labels (ints): raw labels (entity)

        Return:
            ints: updated labels which has the same length as
                  transformed sequence

        """
        for label_aligner in self.collections:
            labels = label_aligner.transform(labels)
        return labels

    def inverse_transform(self, labels: List[int]) -> List[int]:
        """Realign model prediction to its original input

        Arg:
            labels (ints): model prediction (entity)

        Return:
            ints: updated labels which has the same length as
                  original input (utterance)

        """
        for label_aligner in self.collections[::-1]:
            labels = label_aligner.inverse_transform(labels)
        return labels
