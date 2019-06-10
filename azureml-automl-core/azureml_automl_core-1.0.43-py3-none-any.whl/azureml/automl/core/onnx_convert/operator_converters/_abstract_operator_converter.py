# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base abstract operator converter."""
from abc import ABC, abstractmethod

from automl.client.core.common.exceptions import OnnxConvertException


class _AbstractOperatorConverter(ABC):
    """Abstract base class for the operator converters."""

    # Operator alias used by the upper level code, a static base property.
    # Subclasses should override this value in there constructor.
    OPERATOR_ALIAS = '__InvalidAlias__'

    def get_alias(self):
        """
        Get the converter's alias.

        :return: The operator alias of instance of subclasses.
        """
        converter_tp = type(self)
        alias = self.OPERATOR_ALIAS
        # Check if the alias is valid or not.
        if alias == _AbstractOperatorConverter.OPERATOR_ALIAS:
            raise OnnxConvertException('Invalid Operator Alias "{0}" assined '
                                       'in operator converter class {1}'.format(alias, converter_tp))
        return alias

    @abstractmethod
    def setup(self):
        """Abstract method for setting up the converter."""
        raise NotImplementedError
