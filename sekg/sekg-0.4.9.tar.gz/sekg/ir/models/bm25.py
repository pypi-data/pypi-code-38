#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
# from functools import partial
# from multiprocessing import Pool
from pathlib import Path

import gensim
import math
import numpy as np
# from gensim.summarization.bm25 import BM25
# from gensim.utils import effective_n_jobs
from six import iteritems
from sekg.ir.doc.wrapper import PreprocessMultiFieldDocumentCollection
from sekg.ir.models.base import DocumentSimModel
from sekg.util.annotation import catch_exception


# todo: speed up
class BM25Model(DocumentSimModel):
    """
    This class is used the BM25 model to compute the document similarity score.
    The implementation from BM25 is from gensim.
    """
    __bm25_model_name__ = "bm25.model"
    __doc_collection_name__ = "doc.pre.collection"
    __dictionary_name__ = "corpus.dict"

    def __init__(self, name, model_dir_path, **config):

        """
        init the model with model_dir_path:
        """
        super().__init__(name, model_dir_path, **config)

        self.bm25_model = None
        self.corpus = None
        self.dict = None
        self.__init_sub_model_path__()

        self.preprocessor = None
        self.preprocess_doc_collection = None

    def __init_sub_model_path__(self):
        if self.model_dir_path is None:
            return
        model_dir = Path(self.model_dir_path)
        self.bm25_model_path = str(model_dir / self.__bm25_model_name__)
        self.entity_collection_path = str(model_dir / self.__doc_collection_name__)
        self.dictionary_path = str(model_dir / self.__dictionary_name__)
        model_dir.mkdir(parents=True, exist_ok=True)

    def init_model_as_submodel(self):
        """
        init the model
        :return:
        """
        self.init_model()

    @catch_exception
    def init_model(self):
        """
        init the model
        :return:
        """
        self.__init_sub_model_path__()
        print("loading the bm25 models")
        with open(self.bm25_model_path, 'rb') as fr:
            self.bm25_model = pickle.load(fr)

        self.dict = gensim.corpora.Dictionary.load(self.dictionary_path)
        print("All document number: ", self.dict.num_docs)
        print("All words number: ", self.dict.num_pos)

        preprocess_doc_collection = PreprocessMultiFieldDocumentCollection.load(self.entity_collection_path)
        print("load doc.pre.collection finished")
        self.__init_document_collection(preprocess_doc_collection)

    def __init_document_collection(self, preprocess_doc_collection: PreprocessMultiFieldDocumentCollection):
        self.set_preprocess_doc_collection(preprocess_doc_collection)
        self.set_preprocessor(preprocess_doc_collection.get_preprocessor())

    def train_from_doc_collection_with_preprocessor(self, doc_collection: PreprocessMultiFieldDocumentCollection,
                                                    **config):
        print("start training")
        self.__init_document_collection(doc_collection)
        corpus_clean_text = []
        preprocess_multi_field_doc_list = doc_collection.get_all_preprocess_document_list()

        for docno, multi_field_doc in enumerate(preprocess_multi_field_doc_list):
            corpus_clean_text.append(multi_field_doc.get_document_text_words())
        print("corpus len=%d" % len(corpus_clean_text))

        self.dict = gensim.corpora.Dictionary(corpus_clean_text)
        print("Dictionary init complete")
        self.corpus = [self.dict.doc2bow(text) for text in corpus_clean_text]

        print("bm25 Training...")
        self.bm25_model = BM25(corpus=self.corpus)
        print("bm25 compelete...")

    @catch_exception
    def save(self, model_dir_path):
        """
        save model to the model_dir_path
        :param model_dir_path: the dir to save the model
        :return:
        """
        super().save(model_dir_path)
        self.__init_sub_model_path__()

        self.dict.save(self.dictionary_path)
        print("build dictionary in %s" % self.dictionary_path)

        print("save bm25 model into ", self.bm25_model_path)
        with open(self.bm25_model_path, 'wb') as fw:
            pickle.dump(self.bm25_model, fw)

        print("entity collection saving...")
        self.preprocess_doc_collection.save(self.entity_collection_path)
        print(
            "entity collection finish saving , save to %s, %r" % (
                self.entity_collection_path, self.preprocess_doc_collection))

    def get_full_doc_score_vec(self, query):
        """
        score vector is a vector v=[0.5,2.0,3.0], v[0] means that the document 'd'
         whose index is 0 in DocumentCollection, its score with query is 0.5.
        :param query: a str stands for the query.
        :return: get all document similar score with query as a numpy vector.
        """

        full_entity_score_vec = self.get_cache_score_vector(query)
        if full_entity_score_vec is not None:
            return full_entity_score_vec

        query_words = self.preprocessor.clean(query)
        query_bow = self.dict.doc2bow(query_words)
        full_entity_score_vec = np.array(self.bm25_model.get_scores(query_bow))
        self.cache_entity_score_vector(query, full_entity_score_vec)
        return full_entity_score_vec

    def similarity_4_doc_id_pair(self, doc_id1, doc_id2):
        # todo: implement in the base class or set as a abstract class
        # todo: fix this method. Change the BM25 to compute by numpy for speed up
        # todo: add checking for the doc_id1

        doc1 = self.doc_id2doc(doc_id1)
        pos2 = self.doc_id2doc_index(doc_id2)

        if doc1 is None or pos2 is None:
            return 0.0
        words = doc1.get_document_text_words()

        score = self.bm25_model.get_score(words, pos2)

        return score

    def similarity_by_doc_id(self, doc_id):
        """

        :param doc_id:
        :return:
        """
        # todo: implement in the base class or set as a abstract class
        # todo: fix this method. Change the BM25 to compute by numpy for speed up
        doc = self.doc_id2doc(doc_id)
        words = doc.get_document_text_words()
        full_entity_score_vec = np.array(self.bm25_model.get_scores(words))
        return full_entity_score_vec


# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""This module contains function of computing rank scores for documents in
corpus and helper class `BM25` used in calculations. Original algorithm
descibed in [1]_, also you may check Wikipedia page [2]_.


.. [1] Robertson, Stephen; Zaragoza, Hugo (2009).  The Probabilistic Relevance Framework: BM25 and Beyond,
       http://www.staff.city.ac.uk/~sb317/papers/foundations_bm25_review.pdf
.. [2] Okapi BM25 on Wikipedia, https://en.wikipedia.org/wiki/Okapi_BM25



Examples
--------

.. sourcecode:: pycon

    # >>> from gensim.summarization.bm25 import get_bm25_weights
    # >>> corpus = [
    # ...     ["black", "cat", "white", "cat"],
    # ...     ["cat", "outer", "space"],
    # ...     ["wag", "dog"]
    # ... ]
    # >>> result = get_bm25_weights(corpus, n_jobs=-1)


Data:
-----
.. data:: PARAM_K1 - Free smoothing parameter for BM25.
.. data:: PARAM_B - Free smoothing parameter for BM25.
.. data:: EPSILON - Constant used for negative idf of document in corpus.

"""

PARAM_K1 = 1.5
PARAM_B = 0.75
EPSILON = 0.25


class BM25(object):
    """Implementation of Best Matching 25 ranking function.

    Attributes
    ----------
    corpus_size : int
        Size of corpus (number of documents).
    avgdl : float
        Average length of document in `corpus`.
    doc_freqs : list of dicts of int
        Dictionary with terms frequencies for each document in `corpus`. Words used as keys and frequencies as values.
    idf : dict
        Dictionary with inversed documents frequencies for whole `corpus`. Words used as keys and frequencies as values.
    doc_len : list of int
        List of document lengths.
    """

    def __init__(self, corpus):
        """
        Parameters
        ----------
        corpus : list of list of str
            Given corpus.

        """
        self.corpus_size = len(corpus)
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.wf = {}
        self.doc_len = []
        # self._initialize(corpus)
        self._initialize_with_bow(corpus)
        self.word2score = {}
        self.K = (PARAM_K1 * (1 - PARAM_B + PARAM_B * np.array(self.doc_len) / self.avgdl)).tolist()  # document*1
        self.k1 = PARAM_K1 + 1

    def _initialize(self, corpus):
        """Calculates frequencies of terms in documents and in corpus. Also computes inverse document frequencies."""
        # words = list(set([y for x in corpus for y in x]))
        nd = {}  # word -> number of documents with word
        num_doc = 0
        for index, document in enumerate(corpus):
            self.doc_len.append(len(document))
            num_doc += len(document)
            # all_frequencies = dict(zip(words, [0] * len(words)))

            frequencies = {}
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
                # all_frequencies[word] += 1
            self.doc_freqs.append(frequencies)

            for word in frequencies:
                if word not in self.wf.keys():
                    self.wf[word] = []
                self.wf[word].append([index, frequencies[word]])
                if word not in nd:
                    nd[word] = 0
                nd[word] += 1
        self.avgdl = float(num_doc) / self.corpus_size
        # collect idf sum to calculate an average idf for epsilon value
        idf_sum = 0
        # collect words with negative idf to set them a special epsilon value.
        # idf can be negative if word is contained in more than half of documents
        negative_idfs = []
        for word, freq in iteritems(nd):
            idf = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)
        self.average_idf = float(idf_sum) / len(self.idf)

        eps = EPSILON * self.average_idf
        for word in negative_idfs:
            self.idf[word] = eps

    def _initialize_with_bow(self, corpus):
        """Calculates frequencies of terms in documents and in corpus. Also computes inverse document frequencies."""
        nd = {}  # word -> number of documents with word
        num_doc = 0
        for index, document in enumerate(corpus):
            self.doc_len.append(len(document))
            frequencies = {}
            for word, fre in document:
                num_doc += fre
                frequencies[word] = fre
                if word not in nd:
                    nd[word] = 0
                nd[word] += 1
                if word not in self.wf.keys():
                    self.wf[word] = []
                self.wf[word].append([index, fre])
            self.doc_freqs.append(frequencies)
        self.avgdl = float(num_doc) / self.corpus_size
        # collect idf sum to calculate an average idf for epsilon value
        idf_sum = 0
        # collect words with negative idf to set them a special epsilon value.
        # idf can be negative if word is contained in more than half of documents
        negative_idfs = []
        for word, freq in iteritems(nd):
            idf = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)
        self.average_idf = float(idf_sum) / len(self.idf)
        eps = EPSILON * self.average_idf
        for word in negative_idfs:
            self.idf[word] = eps

    def get_score_for_one_word(self, word_one):
        """Calculates score for one word."""
        if word_one not in self.idf.keys():
            return np.zeros(self.corpus_size)
        idf = self.idf[word_one]  # 1*1
        fre_array = np.zeros(self.corpus_size)
        fre_array[np.array(self.wf[word_one])[:, 0]] = np.array(self.wf[word_one])[:, 1]
        corups_arry = fre_array * self.k1 / (fre_array + np.array(self.K)) * idf
        return corups_arry

    def calculate_scores(self, document):
        """Calculates scores for the whole query."""
        # idf_array = np.empty(len(document))  # query_word * 1
        # fre_arrry = np.empty((len(document), self.corpus_size))  # query_word * corpus_size
        # for index, word in enumerate(document):
        #     idf_array[index] = self.idf.get(word, 0)
        #     fre_arrry[index] = self.wf.get(word, [0] * self.corpus_size)
        idf_array = np.array(list(map(lambda x: self.idf.get(x[0], 0), document)))  # query_word * 1
        fre_array = np.zeros((len(document), self.corpus_size))
        for index, item in enumerate(document):
            fre_array[index][np.array(self.wf[item[0]])[:, 0]] = np.array(self.wf[item[0]])[:, 1]
        fre_arrray = fre_array.T  # corpus_size * query_word
        K = np.array([self.K] * len(document)).T
        all_score = np.sum(fre_arrray * self.k1 / (fre_arrray + K) * idf_array, 1)  # corpus_size * 1
        return all_score

    @catch_exception
    def calculate_scores_with_bow(self, document):
        """Calculates scores for the whole query."""
        idf_array = np.array(list(map(lambda x: self.idf.get(x[0], 0), document)))  # query_word * 1
        word_fre_array = np.array(list(map(lambda x: x[1], document)))
        fre_array = np.zeros((len(document), self.corpus_size))
        for index, item in enumerate(document):
            fre_array[index][np.array(self.wf[item[0]])[:, 0]] = np.array(self.wf[item[0]])[:, 1]
        fre_array = fre_array.T  # corpus_size * query_word
        K = np.array([self.K] * len(document)).T
        all_score = np.sum(fre_array * self.k1 / (fre_array + K) * idf_array * word_fre_array, 1)  # corpus_size * 1
        return all_score

    def get_scores(self, document):
        """Computes and returns BM25 scores of given `document` in relation to
        every item in corpus.

        Parameters
        ----------
        document : list of str
            Document to be scored.

        Returns
        -------
        list of float
            BM25 scores.

        """
        # score_array = np.zeros(self.corpus_size)
        # for word in document:
        #     if word not in self.word2score.keys():
        #         # score_word_1 = self.get_scores_ori([word])
        #         score_word = self.get_score_for_one_word(word)
        #         score_array = score_array + score_word
        #         self.word2score[word] = score_word
        #     else:
        #         score_array = score_array + self.word2score[word]
        # return score_array
        return self.calculate_scores_with_bow(document)

    def get_score(self, document, index):
        """Computes BM25 score of given `document` in relation to item of corpus selected by `index`.

        Parameters
        ----------
        document : list of str
            Document to be scored.
        index : int
            Index of document in corpus selected to score with `document`.

        Returns
        -------
        float
            BM25 score.

        """
        score = 0
        doc_freqs = self.doc_freqs[index]
        for word in document:
            if word not in doc_freqs:
                continue
            score += (self.idf[word] * doc_freqs[word] * self.k1
                      / (doc_freqs[word] + self.K[index]))
        return score

    def get_scores_ori(self, document):
        """Computes and returns BM25 scores of given `document` in relation to
        every item in corpus.

        Parameters
        ----------
        document : list of str
            Document to be scored.

        Returns
        -------
        list of float
            BM25 scores.

        """
        scores = np.array([self.get_score(document, index) for index in range(self.corpus_size)])
        return scores

    def get_scores_bow(self, document):
        """Computes and returns BM25 scores of given `document` in relation to
        every item in corpus.

        Parameters
        ----------
        document : list of str
            Document to be scored.

        Returns
        -------
        list of float
            BM25 scores.

        """
        scores = []
        for index in range(self.corpus_size):
            score = self.get_score(document, index)
            if score > 0:
                scores.append((index, score))
        return scores


# def _get_scores_bow(bm25, document):
#     """Helper function for retrieving bm25 scores of given `document` in parallel
#     in relation to every item in corpus.
#
#     Parameters
#     ----------
#     bm25 : BM25 object
#         BM25 object fitted on the corpus where documents are retrieved.
#     document : list of str
#         Document to be scored.
#
#     Returns
#     -------
#     list of (index, float)
#         BM25 scores in a bag of weights format.
#
#     """
#     return bm25.get_scores_bow(document)
#
#
# def _get_scores(bm25, document):
#     """Helper function for retrieving bm25 scores of given `document` in parallel
#     in relation to every item in corpus.
#
#     Parameters
#     ----------
#     bm25 : BM25 object
#         BM25 object fitted on the corpus where documents are retrieved.
#     document : list of str
#         Document to be scored.
#
#     Returns
#     -------
#     list of float
#         BM25 scores.
#
#     """
#     return bm25.get_scores(document)
#
#
# def iter_bm25_bow(corpus, n_jobs=1):
#     """Yield BM25 scores (weights) of documents in corpus.
#     Each document has to be weighted with every document in given corpus.
#
#     Parameters
#     ----------
#     corpus : list of list of str
#         Corpus of documents.
#     n_jobs : int
#         The number of processes to use for computing bm25.
#
#     Yields
#     -------
#     list of (index, float)
#         BM25 scores in bag of weights format.
#
#     Examples
#     --------
#     .. sourcecode:: pycon
#
#         # >>> from gensim.summarization.bm25 import iter_bm25_weights
#         # >>> corpus = [
#         # ...     ["black", "cat", "white", "cat"],
#         # ...     ["cat", "outer", "space"],
#         # ...     ["wag", "dog"]
#         # ... ]
#         # >>> result = iter_bm25_weights(corpus, n_jobs=-1)
#
#     """
#     bm25 = BM25(corpus)
#     import multiprocessing
#     n_processes = multiprocessing.cpu_count() - 1 if multiprocessing.cpu_count() - 1 > n_jobs else n_jobs
#     if n_processes == 1:
#         for doc in corpus:
#             yield bm25.get_scores_bow(doc)
#         return
#
#     get_score = partial(_get_scores_bow, bm25)
#     pool = Pool(n_processes)
#
#     for bow in pool.imap(get_score, corpus):
#         yield bow
#     pool.close()
#     pool.join()
#
#
# def get_bm25_weights(corpus, n_jobs=1):
#     """Returns BM25 scores (weights) of documents in corpus.
#     Each document has to be weighted with every document in given corpus.
#
#     Parameters
#     ----------
#     corpus : list of list of str
#         Corpus of documents.
#     n_jobs : int
#         The number of processes to use for computing bm25.
#
#     Returns
#     -------
#     list of list of float
#         BM25 scores.
#
#     Examples
#     --------
#     .. sourcecode:: pycon
#
#         # >>> from gensim.summarization.bm25 import get_bm25_weights
#         # >>> corpus = [
#         # ...     ["black", "cat", "white", "cat"],
#         # ...     ["cat", "outer", "space"],
#         # ...     ["wag", "dog"]
#         # ... ]
#         # >>> result = get_bm25_weights(corpus, n_jobs=-1)
#
#     """
#     bm25 = BM25(corpus)
#
#     import multiprocessing
#     n_processes = multiprocessing.cpu_count() - 1 if multiprocessing.cpu_count() - 1 > n_jobs else n_jobs
#     if n_processes == 1:
#         weights = [bm25.get_scores(doc) for doc in corpus]
#         return weights
#
#     get_score = partial(_get_scores, bm25)
#     pool = Pool(n_processes)
#     weights = pool.map(get_score, corpus)
#     pool.close()
#     pool.join()
#     return weights
