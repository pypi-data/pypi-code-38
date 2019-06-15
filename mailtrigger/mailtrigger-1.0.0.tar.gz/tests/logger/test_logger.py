# -*- coding: utf-8 -*-

from mailtrigger.logger.logger import Logger


def test_logger():
    logger = Logger()
    assert (logger is not None)
