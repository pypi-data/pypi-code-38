import re
import pandas as pd
import numpy as np
from collections import Counter


class TextPreprocessing:
    """
    Clean and preprocess your text data
    """

    @staticmethod
    def text_case(df, column, case='lower'):
        """
        Perform string manipulation to convert text to/from:
        1. Lower case
        2. Upper case
        3. Capitalize

        Parameters
        ----------
        df : DataFrame
            The df to perform case operation on
        column : string, int
            The column on which the operation has to be performed
        case : string, default 'lower'
            Options: 'lower' , 'upper', 'capitalize'

        Returns
        -------
        List
        """
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert column in df, "The column is not present in the DataFrame, pass a valid column name"

        if case.lower() == 'lower':
            return df[column].apply(lambda x: x.lower()).values.tolist()
        elif case.lower() == 'upper':
            return df[column].apply(lambda x: x.upper()).values.tolist()
        elif case.lower() == 'capitalize':
            return df[column].apply(lambda x: x.capitalize()).values.tolist()
        else:
            return df[column].values.tolist()

    @staticmethod
    def remove_punctuations(df, column, regex=r'[^\w\s]', space=False):
        """
        Clean text, remove punctuations and symbols

        Parameters
        ----------
        df : DataFrame
            The df to perform case operation on
        column : string, int
            The column on which the operation has to be performed
        regex : string, default r'[^\w\s]'
            Pass any regex to clean the text (punctuations) else leave default
        space : Boolean, default False
            If True, replaces with a space

        Returns
        -------
        List
        """
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert column in df, "The column is not present in the DataFrame, pass a valid column name"

        if space:
            return df[column].apply(lambda x: re.sub(regex, ' ', x)).values.tolist()
        else:
            return df[column].apply(lambda x: re.sub(regex, '', x)).values.tolist()

    @staticmethod
    def remove_digits(df, column):
        """
        Clean text, remove digits

        Parameters
        ----------
        df : DataFrame
            The df to perform case operation on
        column : string, int
            The column on which the operation has to be performed
        Returns
        -------
        List
        """
        
        return df[column].apply(lambda x: ' '.join([x for x in x.split() if not x.isdigit()])).values.tolist()

    @staticmethod
    def remove_characters(df, column, char=2):
        """
        Clean text, remove char

        Parameters
        ----------
        df : DataFrame
            The df to perform case operation on
        column : string, int
            The column on which the operation has to be performed
        char : int
            Characters below this threshold will be removed 
            
        Returns
        -------
        List
        """
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert column in df, "The column is not present in the DataFrame, pass a valid column name"

        return df[column].apply(lambda x: ' '.join([x for x in x.split() if len(x.strip()) > char]))

    @staticmethod
    def remove_stopwords(df, column, **kwargs):
        """
        Remove stopwords from a corpus

        Parameters
        ----------
        df : DataFrame
            The df to perform case operation on
        column : string, int
            The column on which the operation has to be performed
        stopwords : List
            List of stopwords to remove; default list can be found at:
            from toolstack import utils
            stopwords = list(utils.load_stopwords())

        Returns
        -------
        List

        """
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert column in df, "The column is not present in the DataFrame, pass a valid column name"
        assert ('stopwords' in kwargs.keys() or isinstance(kwargs['stopwords'], list)), "Pass a list of 'stopwords'"

        word_list = []
        if 'text_lower' in kwargs.keys() and kwargs['text_lower']:
            for x in np.array(df[column]):
                x = x.split()
                text = ' '.join([s.lower() for s in x if s.lower() not in set(kwargs['stopwords'])])
                word_list.append(text)
            return word_list

        else:
            for x in np.array(df[column]):
                x = x.split()
                text = ' '.join([s for s in x if s.lower() not in set(kwargs['stopwords'])])
                word_list.append(text)
            return word_list


def word_count(df, column, sort='ascending', **kwargs):
    """
    Take the count of unique words

    Parameters
    ----------
    df : DataFrame
        The df to perform case operation on.
    column : string, int
        The column selected should be present in the Dataframe passed
    sort : string, default ascending
        Options: ascending, descending
        If sorted, it will sort values by the count
    stopwords : List
        List of stopwords to remove; default list can be found at:
        from toolstack import utils
        stopwords = list(utils.load_stopwords())

    Returns
    -------
    DataFrame: columns:['Words', 'Count']

    """
    assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
    assert column in df, "The column is not present in the DataFrame, pass a valid column name"

    if 'stopwords' in kwargs.keys():
        assert (isinstance(kwargs['stopwords'], list)), "Pass a list of 'stopwords'"
        word_counter = []
        for x in np.array(df[column]):
            x = x.split()
            for word in x:
                if word.lower() not in set(kwargs['stopwords']):
                    word_counter.append(word.lower())
        k_v = Counter(word_counter)
    else:
        word_counter = []
        for x in np.array(df[column]):
            x = x.split()
            for word in x:
                word_counter.append(word.lower())
        k_v = Counter(word_counter)

    if sort == 'ascending':
        return (pd.DataFrame({'Words': [x for x in k_v.keys()], 'Count': [x for x in k_v.values()]})).sort_values(
            'Count')
    elif sort == 'descending':
        return (pd.DataFrame({'Words': [x for x in k_v.keys()], 'Count': [x for x in k_v.values()]})).sort_values(
            'Count', ascending=False)
    else:
        return pd.DataFrame({'Words': [x for x in k_v.keys()], 'Count': [x for x in k_v.values()]})


class AutomatedTextPreprocessing(TextPreprocessing):

    """
    Perform Automated Data Pre-processing on textual data.

    Parameters
    ----------
    df : DataFrame
        The df to perform case operation on.
    column : List
        The columns in the list should be present in the Dataframe passed

    """

    def __init__(self, df, columns):
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert isinstance(columns, list), "Columns has to a list of columns in the DataFrame passed"
        for column in columns:
            assert column in df, f"The column '{column}' is not present in the DataFrame, pass a valid column name"

        super(AutomatedTextPreprocessing, self).__init__()
        self.df = df.copy()
        self.columns = columns
        self.stopwords = set(pd.read_csv('https://algs4.cs.princeton.edu/35applications/stopwords.txt', header=-1)[0].values.tolist())
        self.char = 2

    def stack(self):
        for column in self.columns:
            if self.df[column].dtype == 'O':
                self.df[column] = self.text_case(self.df, column)
                self.df[column] = self.remove_punctuations(self.df, column)
                self.df[column] = self.remove_digits(self.df, column)
                self.df[column] = self.remove_characters(self.df, column, char=self.char)
                self.df[column] = self.remove_stopwords(self.df, column, stopwords=list(self.stopwords))

        return self.df
