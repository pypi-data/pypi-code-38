import abc
from collections import namedtuple
from typing import List


class OperatorTestTemplate(abc.ABC):

    """Common tests for Operators

    Input pytest parametrization should have 4 input arguments, including
    input_sequence, input_labels, output_sequence, output_labels.
    """
    allowed_fixtures = ['input_sequence', 'input_labels', 'output_sequence', 'output_labels']
    ParamTuple = namedtuple('ParamTuple', allowed_fixtures + ['id'])

    @property
    @abc.abstractmethod
    def params(self) -> List[ParamTuple]:
        pass

    def pytest_generate_tests(self, metafunc):
        # intersection
        needed_args = list(set(self.allowed_fixtures) & set(metafunc.fixturenames))

        if not needed_args:
            return

        def choose_needed_param(param):
            return [getattr(param, key) for key in needed_args]

        needed_params = [
            choose_needed_param(param)
            for param in self.params
        ]
        ids = [param.id for param in self.params]
        metafunc.parametrize(needed_args, needed_params, ids=ids, scope="class")

    @abc.abstractmethod  # fixture
    def op(self):
        pass

    def test_data(self, input_sequence, input_labels, output_sequence, output_labels):
        assert len(input_sequence) == len(input_labels)
        assert len(output_sequence) == len(output_labels)

    def test_transform(self, input_sequence, output_sequence, op):
        output = op.transform(input_sequence)
        assert output_sequence == output[0]

    def test_transform_labels(self, input_sequence, input_labels, output_labels, op):
        _, label_aligner = op.transform(input_sequence)
        output = label_aligner.transform(input_labels)
        assert output_labels == output

    def test_inverse_transform_labels(self, input_sequence, input_labels, output_labels, op):
        _, label_aligner = op.transform(input_sequence)
        output = label_aligner.inverse_transform(output_labels)
        assert input_labels == output

    def test_str(self, op):
        assert str(op).startswith(op.__class__.__name__)


ParamTuple = OperatorTestTemplate.ParamTuple
