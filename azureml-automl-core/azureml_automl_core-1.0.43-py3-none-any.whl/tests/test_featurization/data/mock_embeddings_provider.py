from typing import Any, Optional

import numpy as np

from azureml.automl.core.featurizer.transformer.data import AbstractWordEmbeddingsProvider


class MockWordEmbeddingsProvider(AbstractWordEmbeddingsProvider):
    """Mock word embeddings provider for test usage."""

    def _get_model(self) -> Any:
        self.initialize()
        return self._model

    def _is_lower(self):
        pass

    def __init__(self, vector_size=10):
        """Mock word embeddings provider."""
        self._vector_size = vector_size
        super().__init__("")

    def _get_vector_size(self):
        """Gets vector size."""
        return self._vector_size

    def initialize(self) -> None:
        """
        Overridden method of the base class.

        :return: None
        """
        self._model = {}
        for i in range(self.vector_size):
            self._model[str(i)] = np.random.rand(self.vector_size)
