# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import logging
import signal


def configure_logging():

    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(
        fmt="{levelname:8} {name:22} {message}", style="{"
    )
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(stream_formatter)

    file_handler = logging.FileHandler("debug.log", mode="w")
    file_formatter = logging.Formatter(
        fmt="{relativeCreated:7.0f} {levelname:8} {name:22} {message}",
        style="{",
    )
    file_handler.setFormatter(file_formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)


def context_logger(name):

    logger = logging.getLogger(name)

    def log(description):
        logger.info(description + "...")
        try:
            yield
        except:
            logger.error(description + "... failed")
            raise
        logger.info(description + "... done")

    return contextlib.contextmanager(log)


class NonZeroExitCode(Exception):
    pass


def signal_name(signal_number):
    return signal.Signals(signal_number).name


@contextlib.contextmanager
def print_test_result():
    logger = logging.getLogger(__name__)
    try:
        yield
    except:
        logger.error("Test failed")
        raise
    logger.info("Test passed")


@contextlib.contextmanager
def trace_test_environment():
    logger = logging.getLogger(__name__)
    logger.info("Enter test environment")
    try:
        yield
    except:
        logger.error("Exit test environment with failure")
        raise
    logger.info("Exit test environment with success")
