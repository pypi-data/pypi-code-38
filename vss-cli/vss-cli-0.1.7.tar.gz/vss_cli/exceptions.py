"""The exceptions used by VSS CLI."""
from pyvss.exceptions import VssError


class VssCliError(Exception):
    """General VSS CLI exception occurred."""


class ValidationError(Exception):
    """Validation error exception"""
