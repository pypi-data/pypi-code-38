from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
import string
from nltk.corpus import stopwords


def create_stop_words(add_two_letters=True, user_defined=None):
    """ Create a list of stop words

    Stop words are words to be removed from a corpus. The words can be common to most texts, such as 'he/she', or
    specific to a specific corpus. In basketball articles, one might remove the word 'basketball' .

    Parameters
    ----------
    add_two_letters : bool, optional (default=True)
        add all two letter combinations all single letters to the list

    user_defined : list
        user defined list of stop words to add

    Returns
    -------
    stop_words : list, shape = [n_words]
        final list of stop words

    Example
    -------
    create_stop_words(add_two_letters=True, user_defined=['basketball', 'michael', 'best'])

    Reference
    ---------
    https://en.wikipedia.org/wiki/Stop_words
    """

    stop_words = text.ENGLISH_STOP_WORDS.union(stopwords.words('english'))
    if add_two_letters:
        two_letters = []
        for i in string.ascii_lowercase:
            stop_words = stop_words.union(i)
            for j in string.ascii_lowercase:
                two_letters.append(i + j)
                stop_words = stop_words.union(two_letters)
    if user_defined:
        stop_words = stop_words.union(user_defined)

    return stop_words


def clean_text(text_column, stop_words=None, remove_digits=True, remove_punctuation=True):
    """ Clean the column of text in your dataframe

    Plain text is difficult to perform analysis on. Here, we complete several preprocessing steps used when working
    with text. We convert to lower case, remove stop words, digits, and punctuation.

    Users who wish to clean their text in a different manner, need only not to run this function.

    Parameters
    ----------
    text_column : Series, shape [n_documents]
        A pandas Series containing cleaned text for each article

    stop_words : list, shape = [n_words]
        options list of stop words - can be created with create_stop_words()

    remove_digits : bool, optional (default=True)
        True if all digits should be removed

    remove_punctuation : bool, optional (default=True)
        True is all punctuation should be removed

    Returns
    -------
    df : DataFrame, shape [n_documents, m_columns]


    Example
    -------
    from random import choice
    chars = string.ascii_letters + string.punctuation + string.digits + "              "
    a = []
    for i in range(5):
        a.append("".join(choice(chars) for x in range(200)))
    text_column = pd.Series(a)
    clean_text(text_column)
    """

    # ----- To lower
    text_column = text_column.str.lower()

    # ----- Remove punctuation
    punctuation = string.punctuation + '“' + '”' + "—"  # This is not a dash. Do not remove it.
    if remove_punctuation:
        for symbol in punctuation:
            text_column = text_column.str.replace(symbol, ' ')

    # ----- Remove stop words
    if stop_words:
        text_column = text_column.apply(lambda x: [item for item in x.split() if item not in stop_words])
    else:
        text_column = text_column.apply(lambda x: [item for item in x.split()])

    # ----- Remove digits
    if remove_digits:
        text_column = text_column.apply(
            lambda x: ' '.join([word for word in x if not any(c.isdigit() for c in word)]))
    else:
        text_column = text_column.apply(
            lambda x: ' '.join([word for word in x]))  # turn back into string

    return text_column


def create_wc_dict(wc_data, text_column='text_column', min_df=.0005, stop_words=None):
    """ Find the ids of all the documents that have a keyword

    Parameters
    ----------
    wc_data : DataFrame, shape [n_documents, m_columns]
        Dataframe with at least one column being of text documents

    text_column : str
        String specifying the column of text in wc_data

    min_df : float in range [0.0, 1.0] or int, default=1
        When building the vocabulary ignore terms that have a document
        frequency strictly lower than the given threshold. This value is also
        called cut-off in the literature.
        If float, the parameter represents a proportion of documents, integer
        absolute counts.

    stop_words : string {'english'}, list, or None (default)
        If 'english', a built-in stop word list for English is used.
        There are several known issues with 'english' and you should
        consider an alternative (see :ref:`stop_words`).
        If a list, that list is assumed to contain stop words, all of which
        will be removed from the resulting tokens.
        Only applies if ``analyzer == 'word'``.
        If None, no stop words will be used. max_df can be set to a value
        in the range [0.7, 1.0) to automatically detect and filter stop
        words based on intra corpus document frequency of terms.

    Returns
    -------
    wc_dict : dict
        A dictionary containing the objects needed for the WordCount class

    Examples
    --------
    # TODO

    References
    ----------
    https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html

    """

    # --- Unigram vectorizer - All words in less than 1/2000 articles will be dropped
    unigram_cv = CountVectorizer(min_df=min_df, ngram_range=(1, 1), stop_words=stop_words)
    unigram_array = unigram_cv.fit_transform(wc_data[text_column].values)
    # --- Bigram vectorizer - All words in less than 1/2000 articles will be dropped
    bigram_cv = CountVectorizer(min_df=min_df, ngram_range=(2, 2), stop_words=stop_words)
    bigram_array = bigram_cv.fit_transform(wc_data[text_column].values)

    wc_dict = dict()
    wc_dict['wc_data'] = wc_data
    wc_dict['unigram_cv'] = unigram_cv
    wc_dict['unigram_array'] = unigram_array
    wc_dict['bigram_cv'] = bigram_cv
    wc_dict['bigram_array'] = bigram_array

    return wc_dict
