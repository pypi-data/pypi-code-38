import pytest


from ..factory import OperatorFactory


@pytest.fixture
def op_factory():
    yield OperatorFactory()


def test_register(op_factory):
    fake_op = 1
    op_factory.register('1', fake_op)
    assert op_factory['1'] == fake_op


def test_fails_to_register(op_factory):
    fake_op_1 = 1
    fake_op_2 = 2
    op_factory.register('1', fake_op_1)
    with pytest.raises(KeyError):
        op_factory.register('1', fake_op_2)


def test_operator_not_found(op_factory):
    fake_op = 1
    op_factory.register('1', fake_op)

    with pytest.raises(KeyError):
        op_factory['2']
