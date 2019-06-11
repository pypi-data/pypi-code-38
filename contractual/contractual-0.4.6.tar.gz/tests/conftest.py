import pytest

from contractual import ContractMock


@pytest.fixture(autouse=True)
def contract_store():
    yield
    ContractMock.reset_store()
