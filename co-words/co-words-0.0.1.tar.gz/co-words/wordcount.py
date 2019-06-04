from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np

# Authors: Kasey Jones <krjones@rti.orgr>
#          Emily Hadley <ehadley@rti.org>
# License: MIT License


class WordCount:
    """ A class for finding word counts amongst a Series of articles.

    Parameters
    ----------
    wc_dict : dict
        A dictionary containing the data, unigram & bigram CountVectorizers and Arrays

    stop_words : list
        A list of stop words used in the CountVectorizer creation of wc_dict

    """

    def __init__(self, wc_dict, stop_words):

        self.stop_words = stop_words
        # ----- Data
        self.wc_data = wc_dict['wc_data']
        # ----- Documents
        self.unigram_cv = wc_dict['unigram_cv']
        self.unigram_array = wc_dict['unigram_array']
        self.bigram_cv = wc_dict['bigram_cv']
        self.bigram_array = wc_dict['bigram_array']

    def words_occurring_with(self, word_list, when_multiple='OR', return_bigrams=True, doc_count=True, invert=False):
        """ Find words that occur with ....

        Search through all documents and return which documents contain the items in word_list. Users can return
        top unigrams or bigrams

        Parameters
        ----------
        word_list : list, shape[n_words]
            a list of unigrams or bigrams

        when_multiple : string, ['OR', 'AND']
            when multiple words, use 'OR' for articles containing either word, and 'AND' for articles containing both

        return_bigrams : bool, optional (default=True)
            Use True to return the top bigrams occurring with 'words'

        doc_count : bool, optional (default=True)
            Use True to return the number or articles, or False to return the total number of occurrences. For example,
            'hello' might occur 370 times in 100 articles, but it might only occur in 95 of those 100 articles.
            True will return 95, false will return 370.

        invert : bool, optional (default=True)
            Use True to find only documents that do not have the list of words

        Returns
        -------
        output : dictionary
            words : list of tuples sorted by most frequent
            document_ids : list of document ids that the words occur in

        Example
        -------
        # TODO
        """

        final_rows = None
        for word in word_list:
            use_rows = self.find_document_ids(word, invert=invert)
            if not final_rows:
                final_rows = use_rows
            elif when_multiple == 'OR':
                final_rows = list(set().union(use_rows, final_rows))
            else:
                final_rows = list(set(use_rows).intersection(final_rows))

        cv, array = self._assign_cv_array(bigrams=return_bigrams)
        new_array = array.tocsr()[list(set(final_rows)), :]

        if doc_count:
            new_array[new_array > 0] = 1

        docs = list(set(final_rows))
        output = dict()
        output['words'] = word_counts(cv, new_array)
        output['document_ids'] = docs

        return output

    def top_words(self, index=None, bigrams=False, doc_count=False, max_return=25000):
        """ Return the top words of the documents

        Parameters
        ----------
        index : list, optional (default=None)
            A list of indices, or a range. Used to filter the documents.

        bigrams : bool, optional (default=False)
            Use True to return bigrams, False to return unigrams

        doc_count : bool, optional (default=True)
            Use True to return the number or articles, or False to return the total number of occurrences. For example,
            'hello' might occur 370 times in 100 articles, but it might only occur in 95 of those 100 articles.
            True will return 95, false will return 370.

        max_return : Int, optional (default=25000)
            Return the top <max_return> words

        Returns
        -------
        counts : List of tuples
            A list containing all words in cv and their associated counts from the provided array

        Example
        -------
        # TODO

        """
        cv, array = self._assign_cv_array(bigrams=bigrams)
        # doc_count: count documents the word is used in - not total count of words
        if doc_count:
            array[array > 0] = 1
        if index:
            array = array[index, ]
        counts = word_counts(cv, array)[0:max_return]

        return counts

    def co_occur_counts(self, word_list):

        """ return the number of documents containing a list of words

        Parameters
        ----------
        word_list : list
            a list of unigrams or bigrams

        Returns
        -------
        word_list : original input words

        output : Int

        Example
        -------
        wc = WordCount()
        wc.co_occur_counts(['friends', 'low'])
        (['friends', 'low'], 24)
        """

        output = self.words_occurring_with(word_list=word_list, when_multiple='AND', doc_count=True)
        return word_list, output['words'][0][1]

    def _assign_cv_array(self, word=None, bigrams=None):
        """ Assign cv and array

        Which was built to save space when assigning cv and array

        Parameters
        ----------
        word : str
            A word to lookup. Must be one (unigram) or two words (bigram)

        Returns
        -------
        cv : CountVectorizer
        array : array, shape [n_documents, m_words]
        """
        if word:
            if len(word.split()) == 2:
                cv, array = self.bigram_cv, self.bigram_array
            else:
                cv, array = self.unigram_cv, self.unigram_array
        elif bigrams:
            cv, array = self.bigram_cv, self.bigram_array
        else:
            cv, array = self.unigram_cv, self.unigram_array

        return cv, array.copy()

    def find_document_ids(self, words, when_multiple='OR', invert=False):
        """ Find document numbers for a given word

        Parameters
        ----------
        words : str or list
            A word to lookup. Must be one (unigram) or two words (bigram)
            OR a list of words to lookup. Will return only ids containing all words

        when_multiple : string, ['OR', 'AND']
            when multiple words, use 'OR' for articles containing either word, and 'AND' for articles containing both

        invert : bool, optional (default=True)
            Set to True to find only documents that do not have the keyword

        Returns
        -------
        counts : List of tuples
            A list containing all words in cv and their associated counts from the provided array

        """
        if isinstance(words, list):
            ids = None
            for word in words:
                cv, array = self._assign_cv_array(word=word)
                if ids:
                    if when_multiple == 'OR':
                        ids = list(set().union(ids, find_document_ids_one_word(word, cv, array, invert=invert)))
                    else:
                        ids = ids.intersection(find_document_ids_one_word(word, cv, array, invert=invert))
                else:
                    ids = set(find_document_ids_one_word(word, cv, array, invert=invert))

            return list(ids)

        cv, array = self._assign_cv_array(word=words)

        return find_document_ids_one_word(words, cv, array, invert=invert)


def word_counts(cv, array):
    """ Convert a CountVectorizer and its array into word counts

    Parameters
    ----------
    cv : CountVectorizer
        An object of type CountVectorizer

    array : array, shape = (n_documents, m_words)
        The array produced by CountVectorizer().fit_transform(<array_of_documents>)

    Returns
    -------
    counts : List of tuples
        A list containing all words in cv and their associated counts from the provided array

    Example
    -------
    pds = pd.Series(["row row row your boat", "gently down the stream",
                 "merrily merrily merrily merrily", "life is but a dream"])
    unigram_cv = CountVectorizer(min_df=.1, ngram_range=(1, 1))
    unigram_array = unigram_cv.fit_transform(pds.values)
    word_counts(unigram_cv, unigram_array)
    [('merrily', 4),
     ('row', 3),
     ...)]

    References
    ----------
    https://en.wikipedia.org/wiki/Word_count

    """
    counts = list(zip(cv.get_feature_names(), np.asarray(array.sum(axis=0)).ravel()))

    return sorted(counts, key=lambda x: -x[1])


def find_document_ids_one_word(keyword, cv, array, invert=False):
    """ Find the ids of all the documents that have a keyword

    Parameters
    ----------
    keyword : string
        A keyword as a string. Example: "keyword"

    cv : CountVectorizer
        An object of type CountVectorizer

    array : array, shape = (n_documents, m_words)
        The array produced by CountVectorizer().fit_transform(<array_of_documents>)

    invert : bool, optional (default=True)
        Set to True to find only documents that do not have the keyword

    Returns
    -------
    counts : List of tuples
        A list containing all words in cv and their associated counts from the provided array

    Example
    -------
    pds = pd.Series(["row row row your boat", "gently down the stream",
             "merrily merrily merrily merrily", "life is but a dream"])
    unigram_cv = CountVectorizer(min_df=.1, ngram_range=(1, 1))
    unigram_array = unigram_cv.fit_transform(pds.values)
    find_document_ids('merrily', unigram_cv, unigram_array)
    [2]
    """
    if keyword not in cv.vocabulary_:
        print(keyword + ' is not in cv object. Returning an empty list.')
        return []

    word_location = cv.vocabulary_[keyword]

    rows = array[:, word_location] > 0
    if invert:
        rows = np.array([not i for i in rows[0, ]])

    return rows.nonzero()[0].tolist()


def filter_wc_dict(wc_dict, column='', value=''):
    """ Find the ids of all the documents that have a keyword
    DO NOT DELETE.

    Parameters
    ----------
    wc_dict : dict
        A dictionary containing the objects needed for the WordCount class

    column : str
        String in wc_dict['wc_data'] used to filter the data

    value : str, int, etc.
        Value in column to filter to

    Returns
    -------
    wc_dict : dict
        A dictionary containing the objects needed for the WordCount class - filtered by column and value

    Examples
    --------
    # TODO

    """
    wc_dict_copy = wc_dict.copy()

    if isinstance(value, str):
        value = [value]
    keep_rows = wc_dict_copy['wc_data'][column].isin(value)
    # Based on T/F - Filter
    wc_dict_copy['wc_data'] = wc_dict_copy['wc_data'][keep_rows].reset_index(drop=True)
    wc_dict_copy['unigram_array'] = wc_dict_copy['unigram_array'][np.asarray(keep_rows)]
    wc_dict_copy['bigram_array'] = wc_dict_copy['bigram_array'][np.asarray(keep_rows)]

    return wc_dict_copy


def make_ordered_list(values):
    """  Make an ordered list of unique values given a list of values.

    Parameters
    ----------
    values : list, shape [n_values]
        values to find uniques and sort

    Returns
    -------
    uniques : list
        A sorted list of unique values from 'values'

    """
    uniques = list(set(values))
    uniques.sort()
    return uniques


def words_occurring_with_loop(wc_dictionaries, kwargs):
    """ Loop over WordCount objects and get word or document counts

    Parameters
    ----------
    wc_dictionaries : dict
        a dictionary of wc_dict objects

    kwargs : dict
        arguments to be passed to words_occurring_with function

    Returns
    -------
    words : list
        A list of the words occurring with word_list for each of the dictionaries in wc_dictionaries
    docs : list
        A list of the document ids that the word_list occurred in

    Example:
    # TODO
    loop_results = words_occurring_with_loop(wc_objects, kwargs={'word_list': ['jones']})

    :return:
    """
    words, docs = list(), list()
    for item in wc_dictionaries:
        result = wc_dictionaries[item].words_occurring_with(**kwargs)
        words.append(result['words'])
        docs.append(result['document_ids'])

    df = merge_loop_results(words, wc_dictionaries)
    return df, docs


def merge_loop_results(loop_results, wc_dictionaries, max_return=10000):
    """ Create a clean output for words_occurring_with_loop

    Parameters
    ----------
    loop_results : list
        A list containing output words_occurring_with_loop

    wc_dictionaries : dict
        a dictionary of wc_dict objects

    max_return : int, >0
        An int specifying to only return the top overall 'max_return' words

    Returns
    -------
    df : DataFrame
        A pandas DataFrame with merged results from the dictionary of wc_dict objects

    Example
    -------
    # TODO
    merge_loop_results(loop_results)

    """

    # ----- Create the Dataframe output
    df = pd.DataFrame()
    for i in range(len(loop_results)):
        value = loop_results[i]
        term, count = [word[0] for word in value], [count[1] for count in value]
        d_frame = pd.DataFrame(index=term, columns={list(wc_dictionaries.keys())[i]}, data=count)
        if i == 0:
            df = d_frame
        else:
            df = pd.concat([df, d_frame], axis=1)

    # ----- Clean-up the output
    df['total'] = df.sum(axis=1)
    df = df.sort_values('total', ascending=0)
    df[np.isnan(df)] = 0

    return df[0:max_return]


def co_occur_count_loop(wc_dictionaries, word_list):
    """ Count how many times words occur together over several wc_dict objects

    Parameters
    ----------
    wc_dictionaries : dict
        a dictionary of wc_dict objects

    word_list : list, shape[n_words]
        a list of unigrams or bigrams

    Returns
    -------
    df : DataFrame
        A pandas DataFrame with number of times the words appeared in the same document per wc_dict in wc_dictionaries

    Example:
    co_occur_count_loop(wc_objects, ['jones', 'pig']
    """

    loop_result = list()
    for item in wc_dictionaries:
        loop_result.append([word_list, wc_dictionaries[item].co_occur_counts(word_list=word_list)[1]])

    # ----- Convert list into DataFrame
    df = pd.DataFrame()
    keys = list(wc_dictionaries.keys())
    df['word_list'] = [loop_result[0][0]]
    for i in range(len(loop_result)):
        df[keys[i]] = [loop_result[i][1]]
    df['Total'] = df.sum(axis=1)

    return df.set_index('word_list')


def top_words_loop(wc_dictionaries, kwargs):
    """ Find the top words used across all wc_dict objects in wc_dictionaries

    Parameters
    ----------
    wc_dictionaries : dict
        a dictionary of wc_dict objects

    kwargs : dict
        specify any additional arguments that should be passed to top_words function

    Returns
    -------
    df : DataFrame
        A pandas DataFrame with merged results from the dictionary of wc_dict objects

    Example
    -------
    # TODO
    top_words_loop(loop_results)
    """

    loop_result = []
    for item in wc_dictionaries:
        loop_result.append(wc_dictionaries[item].top_words(**kwargs))

    df = merge_loop_results(loop_result, wc_dictionaries)

    return df


def find_document_ids_loop(wc_dictionaries, kwargs, return_counts=True):
    values = []
    quarters = []
    for quarter in wc_dictionaries:
        quarters.append(quarter)
        if return_counts:
            values.append(len(wc_dictionaries[quarter].find_document_ids(**kwargs)))
        else:
            values.append(wc_dictionaries[quarter].find_document_ids(**kwargs))

    df = pd.DataFrame([quarters, values]).T
    if return_counts:
        df.columns = ['Quarter', 'Count']
    else:
        df.columns = ['Quarter', 'Articles']

    return df
