# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""IoC container for data providers."""
from typing import Any, Dict, Optional

from .abstract_wordembeddings_provider import AbstractWordEmbeddingsProvider
from .automl_wordembeddings_provider import AutoMLEmbeddingsProvider
from .word_embeddings_info import EmbeddingInfo


class DataProviders:
    """IoC container for data providers."""

    @classmethod
    def get(cls, embeddings_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Get data provider based on embedding name.

        :param embeddings_name: Name of the embeddings.
        """
        if embeddings_name in EmbeddingInfo._all_:
            factory_method = getattr(cls, embeddings_name)
            if factory_method:
                return factory_method(*args, **kwargs)

        return None

    @classmethod
    def wiki_news_300d_1M_subword(cls, *args: Any, **kwargs: Any) -> AutoMLEmbeddingsProvider:
        """Create fast text based word embeddings provider."""
        return AutoMLEmbeddingsProvider(*args, **kwargs)
