# test_capitalize.py
import pytest
import os
import logging

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    my_path = os.path.join(__file__, "../", "example", "logging.conf")
    monkeypatch.setenv('BAMBOO_LOGGER_CONF', str(my_path))
    from importlib import reload


# def test_basic_logger():
#     from bamboo_lib.logger import logger
#     assert logger.getEffectiveLevel() == logging.INFO
