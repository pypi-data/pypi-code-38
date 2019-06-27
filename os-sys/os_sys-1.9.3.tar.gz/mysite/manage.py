#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('SERVER_SETTINGS_MODULE', 'mysite.settings')
    try:
        from server.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Server. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
