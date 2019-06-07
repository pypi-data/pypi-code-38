# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import logging
import os
import pickle
import tarfile
from enum import Enum

import numpy as np
import pandas as pd
from ibm_ai_openscale.utils import install_package
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import (ParameterSampler, RandomizedSearchCV,
                                     train_test_split)
from sklearn.preprocessing import LabelEncoder


class DriftDetection():
    """
        Class to generate information needed for error model generation
        :param training_data_frame: Dataframe comprising of input training data
        :type training_data_frame: DataFrame

        :param score: Customized score function to get prediction and probability array
        :type training_data_frame: function

        :param payload_analytics_input: Input parameters needed for error model creation
        :type payload_analytics_input:dict

        Example:
        drift_detection_input = {
            "feature_columns":<list of feature columns>
            "categorical_columns": <list of categorical columns>
            "label_column": <label column>
            "problem_type": <problem_type>
        }

    """
    RANDOM_STATE = 111

    def __init__(self, training_dataframe, drift_detection_input):
        initial_level = logging.getLogger().getEffectiveLevel()

        updated_level = logging.getLogger().getEffectiveLevel()

        if initial_level != updated_level:
            logging.basicConfig(level=initial_level)

        self.training_data_frame = training_dataframe
        self.drift_detection_input = drift_detection_input
        self.categorical_map = {}
        self.training_labels = []
        self.predicted_labels = []
        self.ddm_features = []
        self.dd_model = None
        self.base_client_accuracy = 0
        self.base_predicted_accuracy = 0
        self._validate_drift_input()

        install_package("tqdm==4.32.1")

    def _validate_drift_input(self):
        problem_type = self.drift_detection_input.get("problem_type")
        drift_supported_problem_types = ["binary", "multiclass"]
        if problem_type not in drift_supported_problem_types:
            raise Exception(
                "Drift detection is not supported for {}. Supported types are:{}".format(problem_type, drift_supported_problem_types))

        columns_from_data_frame = list(self.training_data_frame.columns.values)
        self.label_column = self.drift_detection_input.get("label_column")
        if self.label_column not in columns_from_data_frame:
            raise Exception(
                "'label_column':{} missing in training data".format(self.label_column))

        self.feature_columns = self.drift_detection_input.get(
            "feature_columns")
        if self.feature_columns is None or type(self.feature_columns) is not list or len(self.feature_columns) == 0:
            raise Exception("'feature_columns should be a non empty list")

        check_feature_column_existence = list(
            set(self.feature_columns) - set(columns_from_data_frame))
        if len(check_feature_column_existence) > 0:
            raise Exception("Feature columns missing in training data.Details:{}".format(
                check_feature_column_existence))

        self.categorical_columns = self.drift_detection_input.get(
            "categorical_columns")

        if self.categorical_columns is not None and type(self.categorical_columns) is not list:
            raise Exception(
                "'categorical_columns' should be a list of values")

        # Verify existence of  categorical columns in feature columns
        if self.categorical_columns is not None and len(self.categorical_columns) > 0:
            check_cat_col_existence = list(
                set(self.categorical_columns) - set(self.feature_columns))
            if len(check_cat_col_existence) > 0:
                raise Exception("'categorical_columns' should be subset of feature columns.Details:{}".format(
                    check_cat_col_existence))

    def _validate_score_probabilities(self, probabilities, expected_rows):
        # 1. Validate if probabilities is a numpy array of shape (expected_rows, classes)
        if not(isinstance(probabilities, np.ndarray)):
            raise Exception(
                "The probabilities output of score function is not of type numpy.ndarray.")

        expected_shape = (expected_rows, len(self.training_labels))
        if probabilities.shape != expected_shape:
            raise Exception("The shape of probabilities output of score function is {} but should be {}".format(
                probabilities.shape, expected_shape))

        # 2. Try to convert probabilities to float
        try:
            probabilities = probabilities.astype(float)
        except ValueError:
            raise Exception("The probabilities output of score function is of type `{}` which can not be cast to float.".format(
                probabilities.dtype.name))

        # 3. Validate that all values of probabilities fall between 0 and 1 inclusive.
        if not(np.all(probabilities >= 0)) and not(np.all(probabilities <= 1)):
            raise Exception(
                "The probabilities output of score function does not lie between 0 and 1.")

        return probabilities

    def _validate_score_predictions(self, predictions, expected_rows):
        # 1. Validate if predictions is a numpy array of shape (batch_size, )
        if not(isinstance(predictions, np.ndarray)):
            raise Exception(
                "The predictions output of score function is not of type numpy.ndarray.")

        expected_shape = (expected_rows, )
        if predictions.shape != expected_shape:
            raise Exception("The shape of predictions output of score function is {} but should be {}".format(
                predictions.shape, expected_shape))

        # 2. Try to cast them in same dtype as classnames
        classnames_dtype = np.array(self.training_labels).dtype.name
        predictions_dtype = predictions.dtype.name
        try:
            predictions = predictions.astype(classnames_dtype)
        except ValueError:
            raise Exception("The predictions output of score function is of type '{}' and can not be cast to training labels' type '{}'.".format(
                predictions_dtype, classnames_dtype))

        return predictions

    def _get_probability_dataframe(self, probabilities):
        # Add probabilities of the classes as columns to the dataframe
        prob_df = pd.DataFrame(probabilities, columns=["Probability of Class '{}'".format(
            predicted_label) for predicted_label in self.predicted_labels])
        sorted_probs = np.sort(probabilities)

        # Also add difference between highest probability and second highest
        # probability
        prob_df["Probability Difference Between Top Two Classes"] = sorted_probs[:, -
                                                                                 1:] - sorted_probs[:, -2:-1]
        return prob_df

    def _get_predicted_labels(self, probabilities, predictions):
        """Given probabilities array, total predictions and training labels, this method tries to map each training label
        to an index of the probability array of a prediction. For `n` training labels, this method iterates through probabilities
        and predictions till it finds `n-1` labels. So, for binary problems, it just needs to look at the first row of probabilities
        and predictions to figure out order of predictions. If there are more than 1 empty places left, this will assign the index
        at empty position as class name.

        Arguments:
            probabilities {numpy.ndarray} -- ndarray of shape (samples,features)
            predictions {numpy.ndarray} -- ndarray of shape (samples,)

        Returns:
            list -- List of predicted labels in the user model output.
        """
        predicted_labels = [None] * len(self.training_labels)

        for probability, prediction in zip(probabilities, predictions):
            max_index = np.argwhere(
                probability == np.amax(probability)).flatten()
            if len(max_index) > 1:
                continue

            predicted_labels[max_index[0]] = prediction

            empty_values = sum(
                predicted_label is None for predicted_label in predicted_labels)
            if empty_values == 1:
                idx = predicted_labels.index(None)
                label = (set(self.training_labels) -
                         set(predicted_labels)).pop()
                predicted_labels[idx] = label
                break

        # If there are still None(s) in predicted_labels replace them with index
        predicted_labels = [predicted_label if predicted_label is not None else idx for idx,
                            predicted_label in enumerate(predicted_labels)]

        return predicted_labels

    def _balance_data(self, train, train_y):
        num_correct_predictions = len(train_y[train_y == 1])
        num_incorrect_predictions = len(train_y[train_y == 0])

        if num_correct_predictions > num_incorrect_predictions:
            supplemental_set = train.iloc[train_y[train_y == 0].index]
            supplemental_set_y = pd.Series([0] * len(supplemental_set))
            repeat_num = int(num_correct_predictions /
                             num_incorrect_predictions)
            remaining_num = num_correct_predictions - \
                num_incorrect_predictions * repeat_num
        else:
            supplemental_set = train.iloc[train_y[train_y == 1].index]
            supplemental_set_y = pd.Series([1] * len(supplemental_set))
            repeat_num = int(num_incorrect_predictions /
                             num_correct_predictions)
            remaining_num = num_incorrect_predictions - num_correct_predictions * repeat_num

        new_train = train.append(
            [supplemental_set] * (repeat_num - 1), ignore_index=True)
        new_train_y = train_y.append(
            [supplemental_set_y] * (repeat_num - 1), ignore_index=True)
        new_train = new_train.append(
            supplemental_set.sample(remaining_num),
            ignore_index=True)
        new_train_y = new_train_y.append(
            supplemental_set_y.sample(remaining_num),
            ignore_index=True)
        return new_train, new_train_y

    def _predict(self, input_df, probability_column_name):
        """Makes a prediction against the drift detection model

        Arguments:
            input_df {pandas.DataFrame} -- input dataframe to score/predict
            probability_column_name {str} -- name of probability column in input_df

        Returns:
            pandas.DataFrame -- output dataframe containing all columns from input_df plus `prediction` and `prediction_confidence`
        """
        encoded_df = input_df.copy()
        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(self.categorical_map[feature])
            encoded_df.loc[:, feature] = le.transform(encoded_df[feature])

        encoded_df = pd.concat([encoded_df, self._get_probability_dataframe(
            np.stack(encoded_df[probability_column_name]))], axis=1)

        output_df = input_df.copy()
        output_df["prediction"] = self.dd_model.predict(
            encoded_df[self.ddm_features])
        output_df["prediction_confidence"] = np.max(
            self.dd_model.predict_proba(encoded_df[self.ddm_features]), axis=1)
        return output_df

    def _split_and_score(self, score, input_df, batch_size, progress_bar):
        """Splits the input dataframe into chunks of data dictated by `batch_size` and scores using `score` param

        Arguments:
            score {function} -- function to score
            input_df {pandas.DataFrame} -- training dataframe
            batch_size {int} -- Chunk size. A value of 1000 will mean at max 1000 rows are scored at a time
            progress_bar {bool} -- Flag to enable/disable the progress bar.

        Returns:
            tuple -- probabilities and predictions for entire dataframe
        """
        probabilities = None
        predictions = None
        start = 0
        end = min(batch_size, len(input_df))

        from tqdm import tqdm

        tqdm_bar = tqdm(total=len(input_df), desc="Scoring training dataframe...",
                        unit="rows", dynamic_ncols=True, disable=not(progress_bar))

        while start < len(input_df):
            if probabilities is None and predictions is None:
                probabilities, predictions = score(input_df.iloc[start:end])
                probabilities = self._validate_score_probabilities(
                    probabilities, end-start)
                predictions = self._validate_score_predictions(
                    predictions, end-start)
            else:
                probability_array, prediction_vector = score(
                    input_df.iloc[start:end])
                probability_array = self._validate_score_probabilities(
                    probability_array, end-start)
                prediction_vector = self._validate_score_predictions(
                    prediction_vector, end-start)
                probabilities = np.vstack((probabilities, probability_array))
                predictions = np.hstack((predictions, prediction_vector))
            tqdm_bar.update(n=(end-start))
            start = end
            end = min(start + batch_size, len(input_df))

        tqdm_bar.close()

        return probabilities, predictions

    def generate_drift_detection_model(self, score, optimise=True,
                                       callback=None, progress_bar=True, batch_size=5000):
        """Generates the drift detection model.

        Arguments:
            score {function} -- A function that accepts a dataframe with features as columns and returns a tuple of numpy array
                of probabilities array of shape `(n_samples,n_classes)` and numpy array of prediction vector of shape `(n_samples,)`

        Keyword Arguments:
            optimise {bool} -- If True, does hyperparameter optimisation for the drift detection model (default: {True})
            callback {function} -- A method to call after every iteration. (default: {None})
            progress_bar {bool} -- If True, shows progress bars. (default: {True})
            batch_size {int} -- Number of rows to score at a time. (default: {5000})
        """

        input_df = self.training_data_frame.copy()
        self.training_data_frame = None

        # Split 80 20
        train_df = input_df[self.feature_columns]
        train_y_df = input_df[self.label_column]
        self.training_labels = np.unique(train_y_df)
        train_df, test_df, train_y_df, test_y_df = train_test_split(
            train_df, train_y_df, test_size=0.2, stratify=train_y_df, random_state=DriftDetection.RANDOM_STATE)
        train_df.reset_index(drop=True, inplace=True)
        test_df.reset_index(drop=True, inplace=True)
        train_y_df.reset_index(drop=True, inplace=True)
        test_y_df.reset_index(drop=True, inplace=True)

        # Score the training subset
        if callback:
            callback(DriftModelStage.SCORE_SPLIT_TRN_DATA.value)

        train_probabilities, train_predictions = self._split_and_score(
            score, train_df, batch_size, progress_bar)
        self.predicted_labels = self._get_predicted_labels(
            train_probabilities, train_predictions)

        # Label encoding
        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(train_df[feature])
            train_df.loc[:, feature] = le.transform(train_df[feature])
            self.categorical_map[feature] = le.classes_

        # Prepare training data for drift detection model.
        ddm_train = pd.concat(
            [train_df, self._get_probability_dataframe(train_probabilities)], axis=1)
        self.ddm_features = list(ddm_train.columns)
        ddm_train_y = pd.Series(train_predictions == train_y_df).replace(
            to_replace={True: 1, False: 0})

        # Balance the training data
        ddm_train, ddm_train_y = self._balance_data(ddm_train, ddm_train_y)

        if optimise:
            parameters = {
                "loss": ["deviance"],
                "learning_rate": [0.1, 0.15, 0.2],
                "min_samples_split": np.linspace(0.005, 0.01, 5),
                "min_samples_leaf": np.linspace(0.0005, 0.001, 5),
                "max_leaf_nodes": list(range(3, 12, 2)),
                "max_features": ["log2", "sqrt"],
                "subsample": np.linspace(0.3, 0.9, 6),
                "n_estimators": range(100, 401, 50)
            }

            model_params = {
                "random_state": DriftDetection.RANDOM_STATE,
                "verbose": 0
            }

            randomized_params = {
                "n_iter": 40,
                "scoring": "f1",
                "n_jobs": -1,
                "cv": 3,
                "verbose": 0,
                "random_state": DriftDetection.RANDOM_STATE,
                "return_train_score": True,
                "callback": callback,
                "progress_bar": progress_bar,
                "model_stage": DriftModelStage.CREATE_OPTIMIZED_DRIFT_MODEL.value
            }

            classifier = GradientBoostingClassifier(**model_params)

            clf = CustomRandomSearch(
                classifier, parameters, **randomized_params)
            clf.fit(ddm_train, ddm_train_y)
            self.dd_model = clf.best_estimator_
        else:
            # If total elements are less than 1M, use 0.05 as learning rate
            # else 0.1
            learning_rate = 0.05 if ddm_train.shape[0] * \
                ddm_train.shape[1] < 1000000 else 0.1

            initial_parameters = {
                "random_state": DriftDetection.RANDOM_STATE,
                "learning_rate": learning_rate,
                "n_estimators": 1500,
                "verbose": 0,
                "n_iter_no_change": 5,
                "min_samples_split": 0.005,
                "min_samples_leaf": 0.0005,
                "max_leaf_nodes": 10
            }

            if callback:
                callback(DriftModelStage.CREATE_DRIFT_MODEL.value)
            self.dd_model = GradientBoostingClassifier(**initial_parameters)

            self.dd_model.fit(ddm_train, ddm_train_y)

        # Score the test subset
        if callback:
            callback(DriftModelStage.SCORE_SPLIT_TEST_DATA.value)
        test_probabilities, test_predictions = self._split_and_score(
            score, test_df, batch_size, progress_bar)

        # Calculate base client model accuracy
        self.base_client_accuracy = accuracy_score(test_y_df, test_predictions)

        # Prepare the test data to score against drift detection model
        ddm_test = pd.concat(
            [test_df, self._get_probability_dataframe(test_probabilities)], axis=1)

        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(self.categorical_map[feature])
            ddm_test.loc[:, feature] = le.transform(ddm_test[feature])

        ddm_test_predictions = self.dd_model.predict(ddm_test)
        ddm_test_y = pd.Series(test_predictions == test_y_df).replace(
            to_replace={True: 1, False: 0})

        # Calculate base predicted accuracy
        self.base_predicted_accuracy = sum(
            ddm_test_predictions) / len(ddm_test_predictions)

    @staticmethod
    def create_model_tar(drift_detection_model, path_prefix=".",
                         file_name="drift_detection_model.tar.gz"):
        """Creates a tar file for the drift detection model

        Arguments:
            drift_detection_model {DriftDetectionModel} -- the drift detection model to save

        Keyword Arguments:
            path_prefix {str} -- path of the directory to save the file (default: {"."})
            file_name {str} -- name of the tar file (default: {"drift_detection_model.tar.gz"})

        Raises:
            Exception: If there is an issue while creating directory, pickling the model or creating the tar file
        """
        try:
            os.makedirs(path_prefix, exist_ok=True)

            model_pkl = io.BytesIO(pickle.dumps(drift_detection_model))

            with tarfile.open(file_name, mode="w:gz") as model_tar:
                tarinfo = tarfile.TarInfo("drift_detection_model.pkl")
                tarinfo.size = len(model_pkl.getvalue())
                model_tar.addfile(tarinfo=tarinfo, fileobj=model_pkl)
        except (OSError, pickle.PickleError, tarfile.TarError):
            raise Exception(
                "There was a problem creating tar file for drift detection model.")


class CustomRandomSearch(RandomizedSearchCV):
    _required_parameters = ["estimator", "param_distributions"]

    def __init__(self, estimator, param_distributions, progress_bar=True, callback=None, n_iter=10, scoring=None,
                 n_jobs=None, iid='deprecated', refit=True, cv='warn', verbose=0, pre_dispatch='2*n_jobs',
                 random_state=None, error_score='raise-deprecating', return_train_score=False, model_stage=None):
        self.param_distributions = param_distributions
        self.n_iter = n_iter
        self.random_state = random_state
        self.progress_bar = progress_bar
        self.callback = callback
        self.model_stage = model_stage
        super().__init__(
            estimator=estimator, param_distributions=self.param_distributions,
            n_iter=self.n_iter, random_state=self.random_state,
            scoring=scoring,
            n_jobs=n_jobs, iid=iid, refit=refit, cv=cv, verbose=verbose,
            pre_dispatch=pre_dispatch, error_score=error_score,
            return_train_score=return_train_score)

    def _run_search(self, evaluate_candidates):
        """Search n_iter candidates from param_distributions"""
        from tqdm import tqdm

        params = list(ParameterSampler(self.param_distributions,
                                       self.n_iter, random_state=self.random_state))
        for idx, param in enumerate(tqdm(params, desc="Optimising Drift Detection Model...",
                                         unit="models", dynamic_ncols=True, disable=not(self.progress_bar))):
            evaluate_candidates([param])
            if self.callback:
                stop = self.callback(self.model_stage, progress_step=idx+1,
                                     progress_total_count=len(params))  # idx starts at 0
                if stop:
                    break


class DriftModelStage(Enum):
    """Enumerated type for different stages involved in drift model creation."""
    READ_TRN_DATA = "READ_TRN_DATA"
    SCORE_SPLIT_TRN_DATA = "SCORE_SPLIT_TRN_DATA"
    SCORE_SPLIT_TEST_DATA = "SCORE_SPLIT_TEST_DATA"
    CREATE_DRIFT_MODEL = "CREATE_DRIFT_MODEL"
    CREATE_OPTIMIZED_DRIFT_MODEL = "CREATE_OPTIMIZED_DRIFT_MODEL"
    STORE_DRIFT_MODEL = "STORE_DRIFT_MODEL"
    DRIFT_MODEL_COMPLETE = "DRIFT_MODEL_COMPLETE"
