# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms column using a label encoder to encode categories into numbers."""
from typing import Optional
import logging
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import murmurhash3_32
import numpy as np

from automl.client.core.common import constants
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer
from automl.client.core.common.model_wrappers import _AbstractModelWrapper


class LabelEncoderTransformer(AutoMLTransformer, _AbstractModelWrapper):
    """Transforms column using a label encoder to encode categories into numbers."""

    def __init__(self, hashing_seed_val: int = constants.hashing_seed_value, logger: Optional[logging.Logger] = None):
        """
        Initialize for label encoding transform.

        :param hashing_seed_val: Seed value used for hashing if needed.
        :param logger: Logger to be injected to usage in this class.
        :return:
        """
        super().__init__()
        self._label_encoder = LabelEncoder()
        self._hashing_seed_val = hashing_seed_val
        self._init_logger(logger)

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(LabelEncoderTransformer, self)._to_dict()
        dct['id'] = "labelencoder"
        dct['type'] = 'categorical'
        dct['kwargs']['hashing_seed_val'] = self._hashing_seed_val

        return dct

    @function_debug_log_wrapped
    def fit(self, x, y=None):
        """
        Fit function for label encoding transform which learns the labels.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        # Keep track of the labels
        self._label_encoder.fit(x)
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Label encoding transform categorical data into integers.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray
        :return: Label encoded array of ints.
        """
        # Find the new classes in 'x'
        new_classes = np.unique(x)

        # Check if new classes are being label encoded
        if len(
                np.intersect1d(
                    new_classes,
                    self._label_encoder.classes_)) < len(new_classes):

            # Create a set of new classes that are detected
            new_classes = np.setdiff1d(new_classes,
                                       self._label_encoder.classes_)

            # Walk each entry in x and map the new classes to existing classes
            x_new_with_known_classes = []
            for entry in x:
                if entry in new_classes:
                    # Compute the hash for the entry and then map it to some
                    # existing class
                    entry = self._label_encoder.classes_[
                        (murmurhash3_32(entry,
                                        seed=self._hashing_seed_val)) % len(
                            self._label_encoder.classes_)]

                x_new_with_known_classes.append(entry)

            # It is safe to run label encoder on all the existing classes
            return self._label_encoder.transform(x_new_with_known_classes)

        # Label encode x column
        return self._label_encoder.transform(x)

    def get_model(self):
        """
        Return LabelEncoder model.

        :return: LabelEncoder model.
        """
        return self._label_encoder
