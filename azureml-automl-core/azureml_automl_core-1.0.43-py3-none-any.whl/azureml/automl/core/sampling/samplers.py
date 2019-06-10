# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and methods for sampling."""
from typing import Any, Dict, Optional

from .abstract_sampler import AbstractSampler
from .count_sampler import CountSampler
from automl.client.core.common import constants


class Samplers:
    """Classes and methods for sampling."""

    @classmethod
    def get(cls, sampler_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create and return the request sweeper.

        :param sampler_name: Name of the requested sweeper.
        """
        if hasattr(cls, sampler_name):
            member = getattr(cls, sampler_name)
            if callable(member):
                return member(*args, **kwargs)
        return None

    @classmethod
    def default(cls, *args: Any, **kwargs: Any) -> AbstractSampler:
        """Create and return the default sampler."""
        return cls.count(*args, **kwargs)

    @classmethod
    def count(cls, *args: Any, **kwargs: Any) -> CountSampler:
        """Count based sampler."""
        if not args:
            args = (constants.hashing_seed_value, )

        return CountSampler(*args, **kwargs)
