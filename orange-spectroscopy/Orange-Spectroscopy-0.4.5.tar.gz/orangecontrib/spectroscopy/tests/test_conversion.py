import unittest

import numpy as np
import sklearn.model_selection as ms

import Orange
from Orange.classification import LogisticRegressionLearner
from Orange.evaluation.testing import TestOnTestData
from Orange.evaluation.scoring import AUC

from orangecontrib.spectroscopy.tests.test_preprocess import \
    PREPROCESSORS_INDEPENDENT_SAMPLES, \
    PREPROCESSORS

from orangecontrib.spectroscopy.tests.test_preprocess import SMALL_COLLAGEN

from orangecontrib.spectroscopy.preprocess import Interpolate, \
    Cut, SavitzkyGolayFiltering
from orangecontrib.spectroscopy.data import getx


def separate_learn_test(data):
    sf = ms.ShuffleSplit(n_splits=1, test_size=0.2, random_state=np.random.RandomState(0))
    (traini, testi), = sf.split(y=data.Y, X=data.X)
    return data[traini], data[testi]


def destroy_atts_conversion(data):
    natts = [a.copy() for a in data.domain.attributes]
    ndomain = Orange.data.Domain(natts, data.domain.class_vars,
                                 metas=data.domain.metas)
    ndata = Orange.data.Table(ndomain, data)
    ndata.X = data.X
    return ndata


def odd_attr(data):
    natts = [a for i, a in enumerate(data.domain.attributes) if i%2 == 0]
    ndomain = Orange.data.Domain(natts, data.domain.class_vars,
                                 metas=data.domain.metas)
    return Orange.data.Table(ndomain, data)


class TestConversion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.collagen = SMALL_COLLAGEN

    def test_predict_same_domain(self):
        train, test = separate_learn_test(self.collagen)
        auc = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        self.assertGreater(auc, 0.9) # easy dataset

    def test_predict_samename_domain(self):
        train, test = separate_learn_test(self.collagen)
        test = destroy_atts_conversion(test)
        try:
            from Orange.data.table import DomainTransformationError
            with self.assertRaises(DomainTransformationError):
                LogisticRegressionLearner()(train)(test)
        except ImportError:  # until Orange 3.19
            aucdestroyed = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
            self.assertTrue(0.45 < aucdestroyed < 0.55)

    def test_predict_samename_domain_interpolation(self):
        train, test = separate_learn_test(self.collagen)
        aucorig = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        test = destroy_atts_conversion(test)
        train = Interpolate(points=getx(train))(train) # make train capable of interpolation
        auc = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        self.assertEqual(aucorig, auc)

    def test_predict_different_domain(self):
        train, test = separate_learn_test(self.collagen)
        test = Interpolate(points=getx(test) - 1)(test) # other test domain
        try:
            from Orange.data.table import DomainTransformationError
            with self.assertRaises(DomainTransformationError):
                LogisticRegressionLearner()(train)(test)
        except ImportError:  # until Orange 3.19
            aucdestroyed = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
            self.assertTrue(0.45 < aucdestroyed < 0.55)

    def test_predict_different_domain_interpolation(self):
        train, test = separate_learn_test(self.collagen)
        aucorig = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        test = Interpolate(points=getx(test) - 1.)(test) # other test domain
        train = Interpolate(points=getx(train))(train)  # make train capable of interpolation
        aucshift = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        self.assertAlmostEqual(aucorig, aucshift, delta=0.01)  # shift can decrease AUC slightly
        test = Cut(1000, 1700)(test)
        auccut1 = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        test = Cut(1100, 1600)(test)
        auccut2 = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        test = Cut(1200, 1500)(test)
        auccut3 = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        # the more we cut the lower precision we get
        self.assertTrue(aucorig > auccut1 > auccut2 > auccut3)

    def test_whole_and_train_separete(self):
        """ Applying a preprocessor before spliting data into train and test
        and applying is just on train data should yield the same transformation of
        the test data. """
        data = self.collagen
        for proc in PREPROCESSORS_INDEPENDENT_SAMPLES:
            _, test1 = separate_learn_test(proc(data))
            train, test = separate_learn_test(data)
            train = proc(train)
            test_transformed = Orange.data.Table(train.domain, test)
            np.testing.assert_almost_equal(test_transformed.X, test1.X,
                                           err_msg="Preprocessor " + str(proc))

    def test_predict_savgov_same_domain(self):
        data = SavitzkyGolayFiltering(window=9, polyorder=2, deriv=2)(self.collagen)
        train, test = separate_learn_test(data)
        auc = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        self.assertGreater(auc, 0.85)

    def test_predict_savgol_another_interpolate(self):
        train, test = separate_learn_test(self.collagen)
        train = SavitzkyGolayFiltering(window=9, polyorder=2, deriv=2)(train)
        auc = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        train = Interpolate(points=getx(train))(train)
        aucai = AUC(TestOnTestData(train, test, [LogisticRegressionLearner()]))
        self.assertAlmostEqual(auc, aucai, delta=0.02)

    def test_slightly_different_domain(self):
        """ If test data has a slightly different domain then (with interpolation)
        we should obtain a similar classification score. """
        # rows full of unknowns make LogisticRegression undefined
        # we can obtain them, for example, with EMSC, if one of the badspectra
        # is a spectrum from the data
        learner = LogisticRegressionLearner(preprocessors=[_RemoveNaNRows()])

        for proc in PREPROCESSORS:
            if hasattr(proc, "skip_add_zeros"):
                continue
            # LR that can not handle unknown values
            train, test = separate_learn_test(self.collagen)
            train1 = proc(train)
            aucorig = AUC(TestOnTestData(train1, test, [learner]))
            test = destroy_atts_conversion(test)
            test = odd_attr(test)
            # a subset of points for training so that all test sets points
            # are within the train set points, which gives no unknowns
            train = Interpolate(points=getx(train)[1:-3])(train)  # interpolatable train
            train = proc(train)
            # explicit domain conversion test to catch exceptions that would
            # otherwise be silently handled in TestOnTestData
            _ = Orange.data.Table(train.domain, test)
            aucnow = AUC(TestOnTestData(train, test, [learner]))
            self.assertAlmostEqual(aucnow, aucorig, delta=0.02, msg="Preprocessor " + str(proc))
            test = Interpolate(points=getx(test) - 1.)(test)  # also do a shift
            _ = Orange.data.Table(train.domain, test)  # explicit call again
            aucnow = AUC(TestOnTestData(train, test, [learner]))
            # the difference should be slight
            self.assertAlmostEqual(aucnow, aucorig, delta=0.05, msg="Preprocessor " + str(proc))


class _RemoveNaNRows(Orange.preprocess.preprocess.Preprocess):

    def __call__(self, data):
        mask = np.isnan(data.X)
        mask = np.any(mask, axis=1)
        return data[~mask]
