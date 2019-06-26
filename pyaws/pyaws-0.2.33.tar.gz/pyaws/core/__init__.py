"""
Common AWS Functionality required to support all services
"""

try:

    from pyaws.core.oscodes_unix import exit_codes

except Exception:
    from pyaws.core.oscodes_win import exit_codes
