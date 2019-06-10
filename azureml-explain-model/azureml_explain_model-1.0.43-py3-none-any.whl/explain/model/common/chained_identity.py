# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Redefines a light-weight chained identity, in case we can't take a dependency on azureml-core."""

import logging


class ChainedIdentity(object):
    """The base class for logging information."""

    def __init__(self, **kwargs):
        """Initialize the ChainedIdentity."""
        self._logger = logging.getLogger("azureml").getChild(self.__class__.__name__)
        self._identity = self.__class__.__name__
        super(ChainedIdentity, self).__init__(**kwargs)
