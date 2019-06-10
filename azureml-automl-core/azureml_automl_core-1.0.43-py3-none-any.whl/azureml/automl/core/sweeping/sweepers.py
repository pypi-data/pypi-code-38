# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory for sweepers."""
from typing import Any

from .abstract_sweeper import AbstractSweeper
from .binary_sweeper import BinarySweeper


class Sweepers:
    """Factory for sweepers."""

    @classmethod
    def default(cls, *args: Any, **kwargs: Any) -> AbstractSweeper:
        """
        Create and return the default sweeper.

        :return: Return default sweeper.
        """
        return cls.binary(*args, **kwargs)

    @classmethod
    def get(cls, sweeper_type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create and return the request sweeper.

        :param sweeper_name: Name of the requested sweeper.
        """
        if hasattr(cls, sweeper_type):
            kwargs["sweeper_class"] = sweeper_type
            member = getattr(cls, sweeper_type)
            if callable(member):                 # Check that the member is a callable
                return member(*args, **kwargs)

        return None

    @classmethod
    def binary(cls, *args: Any, **kwargs: Any) -> BinarySweeper:
        """Binary sweeper."""
        return BinarySweeper(*args, **kwargs)
