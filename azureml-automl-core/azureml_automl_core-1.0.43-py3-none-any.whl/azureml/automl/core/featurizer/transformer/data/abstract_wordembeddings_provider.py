# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for providing word embeddings."""

from typing import cast, Any, Optional
from abc import ABC, abstractmethod
import os


class AbstractWordEmbeddingsProvider(ABC):
    """Class for providing word embeddings."""

    def __init__(self, embeddings_name: str):
        """
        Initialize class for providing word embeddings.

        :param embeddings_name: Name of the embeddings asked for.
        """
        self._embeddings_name = embeddings_name
        self._embeddings_pickle_file = None                                 # type: Optional[str]

    @property
    def embeddings_dir(self) -> str:
        """
        Directory in which embeddings need to be stored for downloaded.

        :return: Directory to which embeddings have to be downloaded.
        """
        embeddings_dir = os.path.join(os.getcwd(), "data", "embeddings")
        if not os.path.exists(embeddings_dir):
            os.makedirs(embeddings_dir)
        return embeddings_dir

    @property
    def vector_size(self) -> int:
        """
        Return number of dimensions in the embedding model.

        :return: Number of dimensions in the embedding model.
        """
        return self._get_vector_size()

    @property
    def model(self) -> Optional[Any]:
        """
        Return the embeddings model.

        :return: The embeddings model.
        """
        return self._get_model()

    @property
    def is_lower(self) -> bool:
        """
        Return whether the embeddings trained only on lower cased words.

        :return: Whether the embeddings trained only on lower cased words.
        """
        return cast(bool, self._is_lower())

    @abstractmethod
    def _is_lower(self):
        raise NotImplementedError("Must be overridden by the implementation.")

    @abstractmethod
    def _get_model(self) -> Any:
        """
        Abstract method to be overridden to obtain model.

        :return: Should return the model object.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_vector_size(self) -> int:
        """Abstract method to be overridden to obtain vector size.

        :return: Should return vector size.
        """
        raise NotImplementedError()
