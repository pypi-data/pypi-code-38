# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Constant strings."""


class ExplanationDashboardInterface(object):
    """Dictonary properties shared between the python and javascript object."""
    LOCAL_EXPLANATIONS = "localExplanations"
    PREDICTED_Y = "predictedY"
    TRAINING_DATA = "trainingData"
    GLOBAL_EXPLANATION = "globalExplanation"
    IS_CLASSIFIER = "isClassifier"
    FEATURE_NAMES = "featureNames"
    CLASS_NAMES = "classNames"
    PROBABILITY_Y = "probabilityY"
    TRUE_Y = "trueY"


class WidgetRequestResponseConstants(object):
    """Strings used to pass messages between python and javascript."""
    ID = "id"
    DATA = "data"
    ERROR = "error"
    REQUEST = "request"
