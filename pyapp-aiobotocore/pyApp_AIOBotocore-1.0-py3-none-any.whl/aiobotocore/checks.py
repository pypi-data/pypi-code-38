from pyapp.checks.registry import register

from .factory import session_factory

register(session_factory)
