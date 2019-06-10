# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Explanation dashboard class."""

from .ExplanationWidget import ExplanationWidget
from IPython.display import display
import numpy as np
import pandas as pd
import sys


class ExplanationDashboard(object):
    """The dashboard class, wraps the dashboard component."""

    def __init__(self, explanationObject, learner, dataset):
        """Initialize the Explanation Dashboard.

        :param explanationObject: An object that represents an explanation. It is assumed that it
            has a local_importance_values property that is a 2d array in teh case of regression,
            and 3d array in the case of classification. Dimensions are either samples x features, or
            classes x samples x features. Optionally, it may have a features array that is the string name
            of the features, and a classes array that is the string name of the classes.
        :type explanationObject: object
        :param learner: An object that represents a model. It is assumed that for the classification case
            it has a method of predict_proba() returning the prediction probabilities for each
            class and for the regression case a method of predict() returning the prediction value.
        :type learner: object
        :param dataset:  A matrix of feature vector examples (# examples x # features), the same sampels
            used to build the explanationObject.
        :type dataset: numpy.array or list[][]
        """
        self._widget_instance = ExplanationWidget()
        self._learner = learner
        self._is_classifier = hasattr(learner, 'predict_proba') and learner.predict_proba is not None
        self._dataframeColumns = None
        if isinstance(dataset, pd.DataFrame) and hasattr(dataset, 'columns'):
            self._dataframeColumns = dataset.columns
        try:
            list_dataset = self._convertToList(dataset)
            localExplanations = self._convertToList(explanationObject.local_importance_values)
            globalExplanation = self._convertToList(explanationObject.global_importance_values)
            y_pred = self._convertToList(learner.predict(dataset))
            local_dim = len(np.shape(localExplanations))
            if local_dim != 2 and local_dim != 3:
                display("Error: Unexpected types")
            else:
                dataArg = {
                    "localExplanations": localExplanations,
                    "predictedY": y_pred,
                    "trainingData": list_dataset,
                    "globalExplanation": globalExplanation,
                    "isClassifier": self._is_classifier}
                if hasattr(explanationObject, 'features') and explanationObject.features is not None:
                    dataArg['featureNames'] = self._convertToList(explanationObject.features)
                if hasattr(explanationObject, 'classes') and explanationObject.classes is not None:
                    dataArg['classNames'] = self._convertToList(explanationObject.classes)
                if hasattr(learner, 'predict_proba') and learner.predict_proba is not None:
                    dataArg['probabilityY'] = self._convertToList(learner.predict_proba(dataset))
                self._widget_instance.value = dataArg
                self._widget_instance.observe(self._on_request, names="request")
                display(self._widget_instance)
        except:
            print("Error: ", sys.exc_info()[0])

    def _on_request(self, change):
        try:
            data = change.new["data"]
            if self._dataframeColumns is not None:
                data = pd.DataFrame(data, columns=self._dataframeColumns)
            if (self._is_classifier):
                prediction = self._convertToList(self._learner.predict_proba(data))
            else:
                prediction = self._convertToList(self._learner.predict(data))
            self._widget_instance.response = {"data": prediction, "id": change.new["id"]}
        except:
            self._widget_instance.response = {
                "error": "Model threw exeption while predicting",
                "data": [], "id": change.new["id"]}

    def _show(self):
        display(self._widget_instance)

    def _convertToList(self, array):
        if (isinstance(array, pd.DataFrame)):
            return array.values.tolist()
        if (isinstance(array, np.ndarray)):
            return array.tolist()
        return array
