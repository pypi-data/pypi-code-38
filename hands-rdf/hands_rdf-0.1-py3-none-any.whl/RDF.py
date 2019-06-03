"""
    HAND RDF - Randomized Decision Forest

    Description:
    Class to wrap the use of the hand detector classifier.

    Author:
    Bernat Galmés Rubert

    Year:
    2018

    Universitat de les Illes Balears
"""
import copy
import logging
import os
import pickle

from sklearn.ensemble import RandomForestClassifier
from tqdm import tqdm

from .Model.MultiModels import TrainModels, TestModels
from .helpers import show_stats
from .Model.Config import config

import pandas as pd

log = logging.getLogger(__name__)


class RDF(RandomForestClassifier):

    # Store if the current instance loaded is configured according to
    # the attributes in Config class
    TRAINED = False

    def __new__(cls, *args, **kwargs):
        """
        If exists a file with an object with the same configuration, instead of build it again, it is
        read from the file. Otherwise it is build from scratch.

        :param args:
        :param kwargs:
        :return:
        """
        if os.path.isfile(config.PATH_CLF_FILE):
            with open(config.PATH_CLF_FILE, 'rb') as handle:
                clf = pickle.load(handle)

            RDF.TRAINED = clf.max_depth == config.rf_max_depth and \
                          clf.min_samples_leaf == config.rf_min_samples_leaf and \
                          (clf.n_features_ == config.N_FEATURES or not config.OFFSETS_USE_ALL)

            return clf

        return super(RDF, cls).__new__(cls)

    def __init__(self, n_estimators=0,
                 max_depth=config.rf_max_depth,
                 min_samples_leaf=config.rf_min_samples_leaf):
        super().__init__(
            n_estimators=n_estimators,
            min_samples_leaf=min_samples_leaf,
            criterion="entropy",
            warm_start=True,
            max_depth=max_depth,
            random_state=10,
            n_jobs=1,
            verbose=0
        )
        if not config.OFFSETS_USE_ALL:
            self.feats = list(pd.read_excel(config.FILE_OFFSETS, sheet_name='OFFSETS',
                                            convert_float=True)['feat'])

        else:
            self.feats = None

        self.train(TrainModels(mode='npy'))
        self.test(TestModels(mode='npy'))
        self.store()

    def store(self, path_file: str = config.PATH_CLF_FILE):
        """
        Store the self instance in the file specified by param

        :param path_file: str file path where to store the file
        :return:
        """

        this = copy.deepcopy(self)
        this.__class__ = RandomForestClassifier
        with open(path_file, 'wb') as handle:
            pickle.dump(this, handle)

    def train(self, multi_model: TrainModels):
        """
        Train the RDF with the files that are part of the multi_model param instance.

        :param multi_model: TrainModels
        :return:
        """
        for file, model in tqdm(multi_model):
            X_train, y_train = model[:, :-1], model[:, -1]
            if self.feats is not None:
                X_train = X_train[:, self.feats]
            self.fit(X_train, y_train)

    def test(self, multi_model: TestModels):
        """
        Test the RDF with the files that are part of the multi_model param instance.

        :param multi_model: TestModels
        :return:
        """
        y_real_all = []
        y_pred_all = []

        for file, model in tqdm(multi_model):
            X_test, y_test = model[:, :-1], model[:, -1]
            if self.feats is not None:
                X_test = X_test[:, self.feats]
            y_pred = self.predict(X_test)

            y_real_all.extend(y_test)
            y_pred_all.extend(y_pred)

        return show_stats(y_real_all, y_pred_all)

    def fit(self, X, y, sample_weight=None):
        """
        Fit the RDF with a single matrix X.

        :param X :  array-like or sparse matrix of shape = [n_samples, n_features]
                    The training input samples. Internally, its dtype will be converted
                    to ``dtype=np.float32``. If a sparse matrix is provided, it will be
                    converted into a sparse ``csc_matrix``.

        :param y :  array-like, shape = [n_samples] or [n_samples, n_outputs]
                    The target values (class labels in classification, real numbers in
                    regression).

        :param sample_weight :  array-like, shape = [n_samples] or None
                    Sample weights. If None, then samples are equally weighted. Splits
                    that would create child nodes with net zero or negative weight are
                    ignored while searching for a split in each node. In the case of
                    classification, splits are also ignored if they would result in any
                    single class carrying a negative weight in either child node.
        :return:
        """
        self.n_estimators += config.rf_inc_trees_fit
        super().fit(X, y, sample_weight)

    def predict(self, X):
        """Predict class for X.

        The predicted class of an input sample is a vote by the trees in
        the forest, weighted by their probability estimates. That is,
        the predicted class is the one with highest mean probability
        estimate across the trees.

        Parameters
        ----------
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The input samples. Internally, its dtype will be converted to
            ``dtype=np.float32``. If a sparse matrix is provided, it will be
            converted into a sparse ``csr_matrix``.

        Returns
        -------
        y : array of shape = [n_samples] or [n_samples, n_outputs]
            The predicted classes.
        """
        return super().predict(X)
