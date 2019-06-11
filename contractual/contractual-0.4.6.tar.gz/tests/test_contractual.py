from unittest.mock import DEFAULT

import pytest

from contractual import ContractMock


def test_mock_returns_value():
    m = ContractMock("my_contract")
    m.return_value = 99
    assert m(7) == 99


def test_returns_side_effect():
    m = ContractMock("my_contract")
    m.side_effect = [3, 2, 1]
    assert m(5) == 3
    assert m(6) == 2
    assert m(7) == 1


def test_side_effect_function():
    m = ContractMock("my_contract")
    m.return_value = 99
    m.side_effect = lambda x: 30
    assert m(1) == 30
    assert (
        ContractMock.contract_store.check(
            _contract="my_contract", call="call(1)", response=30
        )
        is True
    )


def test_side_effect_default():
    m = ContractMock("my_contract")
    m.return_value = 99
    m.side_effect = lambda x: DEFAULT
    assert m(1) == 99
    assert (
        ContractMock.contract_store.check(
            _contract="my_contract", call="call(1)", response=99
        )
        is True
    )


def test_records_call_in_store():
    m = ContractMock("my_contract")
    m.return_value = 99
    m(26)
    assert (
        ContractMock.contract_store.check(
            _contract="my_contract", call="call(26)", response=99
        )
        is True
    )


def test_retuns_false_for_missing_call():
    ContractMock("my_contract")
    assert (
        ContractMock.contract_store.check(
            _contract="my_contract", call="call(26)", response=99
        )
        is False
    )


def test_fails_on_conflicting_responses():
    m = ContractMock("my_contract")
    m.return_value = 99
    m(26)
    m.return_value = 35
    with pytest.raises(AssertionError):
        m(26)


def test_method_call_captured():
    m = ContractMock("my_contract")
    m.method.return_value = 99
    assert m.method(26) == 99
    assert (
        ContractMock.contract_store.check(
            _contract="my_contract.method", call="call(26)", response=99
        )
        is True
    )
