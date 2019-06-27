"""
Invokes server-admin when the server module is run as a script.

Example: python -m server check
"""
from server.core import management

if __name__ == "__main__":
    management.execute_from_command_line()
