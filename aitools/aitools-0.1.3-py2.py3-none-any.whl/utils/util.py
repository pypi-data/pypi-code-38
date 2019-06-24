"""
This module contains generic utilities.
"""

# import pandas as pd
import random
import re

from aitools.utils import constant


def is_numeric(value): return isinstance(value, int) or isinstance(value, float)


def create_random_cluster(min_range, max_range, dim, size):
    """
        Worlds most elegant cluster making function.
        Caution: Do not play with this.
    :param min_range: Minimum range of randomly generated value
    :param max_range: Maximum range of randomly generated value
    :param dim: Number of elements in Single Vector
    :param size: Entire size of the vector population
    :return: List of vectors containing all above attributes.
    """
    return [[random.randint(min_range, max_range)
             for _ in range(dim)]
            for _ in range(size)]


def tokenizer(regex, speech):
    """

    :param regex: regular expression for text extraction
    :param speech: speech which needs to be extracted
    :return: array of words which are extracted from speech.
    """
    return re.findall(regex, speech)


def prepare_tokens(speech, regex, stop_words, stemmer):
    """

    :param speech:
    :param regex:
    :param stop_words:
    :param stemmer:
    :return:
    """
    speech = tokenizer(regex, speech.lower())
    string_list = [stemmer.stem(string) for string in speech if string not in stop_words]

    return string_list


def train_test_split(x, y, test_pct):
    data = zip(x, y) # pair corresponding values
    train, test = split_data(data, 1 - test_pct) # split the data set of pairs
    x_train, y_train = zip(*train) # magical un-zip trick
    x_test, y_test = zip(*test)
    return x_train, x_test, y_train, y_test


def split_data(data, prob):
    """split data into fractions [prob, 1 - prob]"""
    results = [], []
    for row in data:
        results[0 if random.random() < prob else 1].append(row)
    return results


def build_feature_frame(independent_features, dependent_feature):

    frame = []
    for X, y in zip(independent_features, dependent_feature):
        X.append(y)
        frame.append(X)

    return frame

# def prepare_data(file_path, label_name):
#     df = pd.read_csv(file_path)
#     cols = list(df.columns.values)
#     cols.pop(cols.index(label_name))
#
#     return df[cols + [label_name]].values.tolist()
