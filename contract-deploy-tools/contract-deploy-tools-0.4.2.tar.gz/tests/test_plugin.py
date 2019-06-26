import pytest


@pytest.fixture()
def contract(deploy_contract):
    return deploy_contract("TestContract", constructor_args=(4,))


def test_call(contract):
    assert contract.functions.testFunction(3).call() == 7
