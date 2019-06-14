#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

logger = logging.getLogger("controll_server")
CONFIG = None

def run(*args):
    try:
        if __name__ == "__main__":
            from controll_server import settings
        else:
            from .controll_server import settings
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",settings.__name__
        )
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(args)
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    run(*sys.argv)
