import pickle
from typing import Optional

from sklearn.base import BaseEstimator


def write(clf: BaseEstimator, path: str) -> None:
    """
    Writes ``sklearn`` classifier to file

    :param clf: instance of classifier
    :param path: path to write classifier
    :return:
    """
    if not isinstance(clf, BaseEstimator):
        raise ValueError('Object to serialise was not an Estimator')

    with open(path, 'wb') as file:
        pickle.dump(clf, file)


def read(path: str) -> Optional[BaseEstimator]:
    """
    Reads ``sklearn`` classifier from file

    :param path: path to read classifier from
    :return: de-serialised classifier
    """
    with open(path, 'rb') as file:
        clf = pickle.load(file)

        if not isinstance(clf, BaseEstimator):
            raise ValueError('De-serialised object was not an Estimator')

        return clf
