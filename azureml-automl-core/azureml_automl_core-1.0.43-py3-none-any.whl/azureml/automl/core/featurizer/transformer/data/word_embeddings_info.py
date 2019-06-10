# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holder for embedding information."""
from typing import cast, Dict, Optional, Tuple


class EmbeddingInfo:
    """Class to hold information of embeddings."""

    ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300 = "wiki_news_300d_1M_subword"

    _all_ = [ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300]

    def __init__(self, user_friendly_name: str, embedding_name: str, download_prefix: str, file_name: str,
                 lower_case: bool, license: str, credits: str, md5hash: str) -> None:
        """
        Create embedding info object.

        :param embedding_name: Name of the embedding.
        :param download_prefix: Prefix of the url to download from.
        :param file_name: Name of the file to be appended to the prefix.
        :param lower_case: True if the embeddings were generated on strings after lower casing.
        """
        self._user_friendly_name = user_friendly_name
        self._embedding_name = embedding_name
        self._download_prefix = download_prefix
        self._file_name = file_name
        self._lower_case = lower_case
        self._license = license
        self._credits = credits
        self._md5hash = md5hash


# TODO Make this a full fledged class and move to config
class WordEmbeddingsInfo:
    """Word embeddings information holder."""

    embeddings = {EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300: EmbeddingInfo(
        user_friendly_name="English word embeddings trained on wikipedia and web",
        embedding_name=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
        download_prefix="https://aka.ms/automl-resources/data/wordvectors/",
        file_name="{base}.pkl".format(base=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300),
        lower_case=False,
        license="Creative Commons Attribution-Share-Alike License (3.0). More information can be found at: "
                "https://creativecommons.org/licenses/by-sa/3.0/",
        credits="Advances in Pre-Training Distributed Word Representations by P. Bojanowski, E. Grave, A. Joulin, "
                "T. Mikolov, Proceedings of the International Conference on Language Resources and Evaluation "
                "(LREC 2018). More information can be found at: https://fasttext.cc and "
                "http://https://arxiv.org/abs/1712.09405",
        md5hash="4fd6dce9765e619aca3d26481076763b")}                            # type: Dict[str, EmbeddingInfo]

    @classmethod
    def get(cls, embeddings_name: str) -> Optional[EmbeddingInfo]:
        """
        Get embedding information given the name.

        :param embeddings_name: Name of the requested embeddings.
        :return: Information on the embeddings.
        """
        return cls.embeddings[embeddings_name] if embeddings_name in cls.embeddings else None
