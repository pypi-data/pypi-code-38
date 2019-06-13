import pytest
import requests


@pytest.fixture(scope='session')
def token_admin():
    return None


@pytest.fixture(scope='session')
def token_simple():
    return None 
