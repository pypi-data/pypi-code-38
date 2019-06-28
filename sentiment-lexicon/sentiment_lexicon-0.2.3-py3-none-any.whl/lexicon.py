from typing import Optional, List, Union, Tuple
from functools import reduce
import pandas as pd
import numpy as np
import multiprocessing as mp


class Lexicon:
    '''A class wrapping a sentiment lexicon.

    Provides a :meth:`value` method for finding the sentiment value of a word.

    Parameters:
        words: List of words.
        values: List of values.
        default: The value given to words that are not in the lexicon.
        normalize: Determines if the values are normalized to [-1, 1].

    Attributes:
        default: The default value.
        data: The lexicon data.
        range: The range that the sentiment values are spanning.

    Raises:
        ValueError: If :obj:`words` and :obj:`values` do not have the same length.

    Examples:
        Creating a lexicon requires one sentiment value per word

        >>> Lexicon(['good'], [1])
        <sentiment_lexicon.lexicon.Lexicon object at ...>

        otherwise an exception is raised.

        >>> Lexicon(['good'], [])
        Traceback (most recent call last):
        ...
        ValueError: words and values must have the same length

        Normalizing the sentiment values is done by passing ``True`` as the ``normalize`` parameter.

        >>> lexicon = Lexicon(['good', 'bad', 'maybe'], [10, -8, 2], normalize=True)
        >>> lexicon.data
        good     1.0
        bad     -0.8
        maybe    0.2
        dtype: float64
    '''
    default: float
    data: pd.Series
    range: Tuple[float, float]

    def __init__(self, words: List[str], values: List[float],
                 default: Optional[float] = None, normalize: Optional[bool] = False):
        if len(words) != len(values):
            raise ValueError('words and values must have the same length')

        self.default = default
        self.data = pd.Series(values, index=words, dtype='float')

        if normalize:
            self.data /= self.data.abs().max()

        self.range = (self.data.min(), self.data.max())

    def value(self, word: str, default: Optional[float] = None) -> float:
        '''Returns the sentiment value of a given word.

        Parameters:
            word: The word to find sentiment value for.
            default: The value to return if not value if found for :obj:`word`.
                Takes precedence over the :obj:`default` attribute of :class:`Lexicon`.

        Raises:
            KeyError: If :obj:`word` is not found in the lexicon and a :obj:`default` is not provided.

        Returns:
            The sentiment value for the word.

        Examples:
            >>> lexicon = Lexicon(['good'], [1])
            >>> lexicon.value('good')
            1.0

            >>> lexicon.value('bad')
            Traceback (most recent call last):
            ...
            KeyError: 'bad not present in the lexicon'

            >>> lexicon = Lexicon(['good'], [1], default=0)
            >>> lexicon.value('bad')
            0

            >>> lexicon.value('bad', default=-1)
            -1
        '''
        default = default if default is not None else self.default

        try:
            return self.data.at[word]
        except KeyError as error:
            if default is not None:
                return default
            else:
                raise KeyError(
                    f'{word} not present in the lexicon') from error

    @staticmethod
    def from_labelled_text(positive: List[str], negative: List[str], min_df: Optional[float] = 0.0,
                           alpha: Optional[float] = 0.5, ignore_case: Optional[bool] = True, **kwargs) -> 'Lexicon':
        '''Generate a :class:`Lexicon` based on positive and negative documents using pointwise mututal information.

        Parameters:
            positive: List of positive documents.
            negative: List of negative documents.
            min_df: The number of documents that a word must occur in before it is added to the lexicon.
            alpha: Determines how much the PMI of the two classes affect each other when computing the sentiment values.
            ignore_case: Determines if the case of the words in the documents are ignored.
                If ``True``, the words `good` and `Good` will be treated as the same.
            kwargs: Parameters passed to the :class:`Lexicon` constructor.

        Examples:
            >>> Lexicon.from_labelled_text(['This is good'], ['This is bad'])
            <sentiment_lexicon.lexicon.Lexicon object at ...>

            >>> Lexicon.from_labelled_text(['This is good'], [])
            Traceback (most recent call last):
            ...
            ValueError: there must be at least one positive and one negative document
        '''
        if len(positive) == 0 or len(negative) == 0:
            raise ValueError(
                'there must be at least one positive and one negative document')

        documents = {'positive': positive, 'negative': negative}
        labels = documents.keys()
        total_columns = [f'{label}_total' for label in labels]

        total_length = sum([len(docs) for docs in documents.values()])

        label_base_rates = pd.Series(
            {label: len(docs) / total_length for label, docs in documents.items()})

        word_count = _add_dataframes([_documents_word_count(
            docs, label, ignore_case=ignore_case) for label, docs in documents.items()]).fillna(0).add(1)

        word_count['total'] = word_count[total_columns].sum(axis='columns')

        # Word base rates. P(W).
        word_count['base_rate'] = word_count['total'] / \
            word_count['total'].sum()

        # Word conditional on label. P(W | L).
        for label in labels:
            word_count[f'{label}_cond_proba'] = word_count[f'{label}_total'] / \
                word_count['total']

        # Word and label joint. P(W, L).
        for label in labels:
            word_count[f'{label}_joint_proba'] = word_count[f'{label}_cond_proba'] * \
                label_base_rates[label]

        # Pointwise mutal information for words and labels. PMI(W, L).
        for label in labels:
            word_count[f'{label}_pmi'] = np.log(
                word_count[f'{label}_joint_proba'] / (word_count['base_rate'] * label_base_rates[label]))

        # Sentiment value for words and label. Sent(W, L).
        for label in labels:
            other_label = next(
                other_label for other_label in labels if other_label != label)
            word_count[f'{label}_sent'] = alpha * word_count[f'{label}_pmi'] - \
                (1 - alpha) * word_count[f'{other_label}_pmi']

        # Find label with highest Sent(W, L) value.
        word_count['label'] = word_count[[
            f'{label}_sent' for label in labels]].idxmax(axis='columns')

        word_count['sent'] = word_count.lookup(
            word_count.index, word_count['label'])

        word_count.loc[word_count['label'] ==
                       'negative_sent', 'sent'] = word_count['sent'] * -1

        return Lexicon(word_count.index, word_count['sent'], **kwargs)


def _add_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    '''Merges a list of :obj:`pd.DataFrames`s and adds the values in common columns.

    Parameters:
        dataframes: The :obj:`pd.DataFrame`s to add.

    Examples:
        >>> df1 = pd.DataFrame({'col1': [1, 1], 'col2': [2, 3]})
        >>> df2 = pd.DataFrame({'col1': [1, 2], 'col3': [3, 4]})
        >>> _add_dataframes([df1, df2])
           col1  col2  col3
        0     2   2.0   3.0
        1     3   3.0   4.0
    '''
    return reduce(lambda acc, current: acc.add(
        current, fill_value=0), dataframes)


def _count_words(document: str,
                 ignore_case: Optional[bool] = True) -> pd.Series:
    '''Counts number of words in a document.

    Parameters:
        document: The document to count the words in.
        ignore_case: Determines if the count is case insensitive.

    Examples:
        >>> _count_words('Count these words')
        count    1
        these    1
        words    1
        dtype: int64

        >>> _count_words('Count these words', ignore_case=False)
        Count    1
        these    1
        words    1
        dtype: int64
    '''
    words = [(word.lower() if ignore_case else word)
             for word in document.split(' ')]
    return pd.Series(words).value_counts().sort_index()


def _helper(partition: List[str], label: str,
            ignore_case: Optional[bool] = False) -> pd.DataFrame:
    return _add_dataframes([_count_words(document, ignore_case=ignore_case).rename(
        f'{label}_total').to_frame().assign(**{f'{label}_doc': 1}) for document in partition])


def _documents_word_count(
        documents: List[str], label: str, ignore_case: Optional[bool] = True) -> pd.DataFrame:
    '''Counts words in multiple :obj:`documents` of a given :obj:`label`.

    Parameters:
        documents: The list of documents to count words in.
        label: The label of the documents.
        ignore_case: Determines if the word count should be case insensitive. Passed to :func:`_count_words`.

    Examples:
        >>> _documents_word_count(['Today is a good day', 'This is good'], 'positive')
               positive_total  positive_doc
        a                 1.0           1.0
        day               1.0           1.0
        good              2.0           2.0
        is                2.0           2.0
        this              1.0           1.0
        today             1.0           1.0
    '''
    with mp.Pool() as pool:
        number_of_partitions = min(len(documents), mp.cpu_count())
        partitions = np.array_split(documents, number_of_partitions)
        word_counts = _add_dataframes(pool.starmap(
            _helper, [(partition, label, ignore_case) for partition in partitions]))

    return word_counts
