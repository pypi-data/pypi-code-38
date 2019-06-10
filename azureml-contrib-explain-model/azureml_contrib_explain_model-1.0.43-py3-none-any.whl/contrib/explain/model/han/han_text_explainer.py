# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Hierarchical Attention Network text explainer for getting model explanations from text data."""

import numpy as np

from azureml.explain.model._internal.common import _sort_values, module_logger
from azureml.explain.model._internal.constants import Tensorflow, ExplainParams, ExplainType
from azureml.explain.model.common.explanation_utils import _convert_to_list
from azureml.explain.model.common.structured_model_explainer import StructuredInitModelExplainer
from ..common.text_explainer_utils import _find_golden_doc
from .han_model import make_data, train_HAN_model, tokenize, make_word2vec_data, \
    HANClassifierModel, HANRegressorModel
from ..explanation.explanation import _create_local_explanation

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap


class HANTextExplainer(StructuredInitModelExplainer):
    """Explain a model trained on a text dataset using a Hierarchical Attention Network DNN."""

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the HANTextExplainer.

        :param model: An object that represents a model. It is assumed that for the classification case
            it has a method of predict_proba() returning the prediction probabilities for each
            class and for the regression case a method of predict() returning the prediction value.
        :type model: object
        :param initialization_examples: A list of text documents.
        :type initialization_examples: list[str]
        """
        super(HANTextExplainer, self).__init__(model, initialization_examples, **kwargs)
        self._logger.debug('Initializing HANTextExplainer')
        self.trained = False
        self.model = model

    def train_model(self, classes=None, word_embedding_path=None, train_epochs=3):
        """Trains a HAN model on the given initialization examples.

        This can be called separately from explain_global if the user prefers to do this as a two-step process.

        :param model: The black box model to explain.
        :type model: model
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :param train_epochs: The number of epochs to train the model on.
        :type train_epochs: int
        """
        # The word embedding size
        EMBEDDING_DIM = 50
        word2vec_model = None
        num_classes = None
        if classes is not None:
            num_classes = len(classes)
        self.is_classifier = True
        try:
            # try to use predict_proba for classification scenario
            probabilities = self.model.predict_proba(self.initialization_examples)
            predictions = probabilities.argmax(axis=1)
            predictions = self.model.predict(self.initialization_examples)
        except AttributeError as ae:
            module_logger.info(
                "predict_proba not supported by given model, assuming regression model and trying predict: " +
                str(ae))
            # try predict since this is a regression scenario
            predictions = self.model.predict(self.initialization_examples)
            self.is_classifier = False
        if word_embedding_path is None:
            # use word2vec if no embedding path specified
            word2vec_model = make_word2vec_data(self.initialization_examples, predictions, EMBEDDING_DIM)
        else:
            make_data(self.initialization_examples, predictions)
        if self.is_classifier:
            self.han_model = HANClassifierModel(classes=num_classes, vocab_size=50001, embedding_size=EMBEDDING_DIM,
                                                word_output_size=100, sentence_output_size=100, device=Tensorflow.CPU0,
                                                learning_rate=1e-4, max_grad_norm=5.0, dropout_keep_proba=0.5,
                                                word_embedding_path=word_embedding_path, word2vec_model=word2vec_model)
        else:
            self.han_model = HANRegressorModel(vocab_size=50001, embedding_size=EMBEDDING_DIM, word_output_size=100,
                                               sentence_output_size=100, device=Tensorflow.CPU0, learning_rate=1e-4,
                                               max_grad_norm=5.0, dropout_keep_proba=0.5,
                                               word_embedding_path=word_embedding_path, word2vec_model=word2vec_model)
        # Run HAN model on initialization examples
        train_HAN_model(self.han_model, train_epochs=train_epochs)
        self.trained = True

    def explain_global(self, evaluation_examples, **kwargs):
        """Explain a model by explaining its predictions on the text document.

        Global explanations are currently not supported, we just return a local explanation
        for explain_global instead on a chosen golden document.
        If multiple documents are passed, we choose the one with the highest predicted probability
        or confidence from the given evaluation examples.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :param tune_epochs: The number of time to tune on the evaluation examples.
        :type tune_epochs: int
        :return: A local explanation of the text document containing the feature importance values,
            expected values and the chosen golden document with highest confidence score in model.
        :rtype: LocalExplanation
        """
        kwargs[ExplainParams.METHOD] = ExplainType.HAN
        return self.explain_local(evaluation_examples, **kwargs)

    def explain_local(self, evaluation_examples, classes=None, tune_epochs=5, **kwargs):
        """Explain a model locally by explaining its predictions on the text document.

        If multiple documents are passed, we choose the one with the highest predicted probability
        or confidence from the given evaluation examples.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :param tune_epochs: The number of time to tune on the evaluation examples.
        :type tune_epochs: int
        :return: A local explanation of the text document containing the feature importance values,
            expected values and the chosen golden document with highest confidence score in model.
        :rtype: LocalExplanation
        """
        # Allow the train step to be done separately since it takes a while
        if not self.trained:
            self.train_model(self.model, self.initialization_examples, classes)

        # find document with highest probability
        if self.is_classifier:
            function = self.model.predict_proba
        else:
            function = self.model.predict
        golden_doc = _find_golden_doc(function, evaluation_examples)
        golden_doc_list = [golden_doc]

        # get diagnostic info prior to tuning for comparison
        shap_values, features = self.han_model.get_feature_importance(golden_doc_list)
        self._sort_shap_values_and_features(shap_values, features)

        # Fine tune the model on the chosen example
        self._fine_tune_model(self.model, golden_doc_list, epochs=tune_epochs)
        shap_values, features = self.han_model.get_feature_importance(golden_doc_list)
        shap_values, shap_imp = self._sort_shap_values_and_features(shap_values, features)
        # convert shap values to numpy array from tuple for consistency
        local_importance_values = _convert_to_list(np.array(shap_values))
        features = list(shap_imp)
        kwargs[ExplainParams.METHOD] = ExplainType.HAN
        if self.is_classifier:
            kwargs[ExplainType.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainType.MODEL_TASK] = ExplainType.REGRESSION
        if self.model is not None:
            kwargs[ExplainParams.MODEL_TYPE] = str(type(self.model))
        else:
            kwargs[ExplainParams.MODEL_TYPE] = ExplainType.FUNCTION
        return _create_local_explanation(local_importance_values=np.array(local_importance_values),
                                         expected_values=None, text_explanation=True,
                                         features=features, classes=classes, **kwargs)

    def _sort_shap_values_and_features(self, shap_values, features):
        """Sorts the shap values and the features according to the ranking of the shap values.

        :param shap_values: The feature importance values from the model.
        :type shap_values: numpy.ndarray
        :param features: The string tokens given to the model.
        :type features: numpy.ndarray
        :return: tuple(shap_values, features)
            where
            - shap_values = The sorted shap values.
            - features = The sorted features according to ranking on shap values.
        :rtype: (numpy.ndarray, numpy.ndarray)
        """
        # flatten to single dimension
        shap_values = shap_values.flatten()
        # find features corresponding to them
        shap_order = shap_values.argsort()[..., ::-1]
        shap_imp = _sort_values(features[0].flatten(), shap_order)
        shap_values = shap_values[shap_order]
        shap_values, shap_imp = zip(*((value, imp) for value, imp in zip(shap_values, shap_imp)
                                      if imp not in ['None', ',', '\n', ':', '\n\n', '-', '.', '(', ')']))
        module_logger.info("shap_values sorted: {}".format(str(shap_values)))
        module_logger.info("features sorted: {}".format(str(shap_imp)))
        return shap_values, shap_imp

    def _fine_tune_model(self, model, evaluation_examples, epochs=1):
        """Fine-tunes the HAN model on the given evaluation examples.

        :param model: The black box model to explain.
        :type model: model
        :param evaluation_examples: The evaluation examples.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param epochs: The number of epochs to fine-tune the model on.
        :type epochs: int
        """
        from sklearn.feature_extraction.text import CountVectorizer
        # Convert document to numeric representation
        vectorizer = CountVectorizer(lowercase=False, min_df=0.0, binary=True)
        vectorizer.fit(evaluation_examples)
        numericData = vectorizer.transform(evaluation_examples)
        numeric_test_data = numericData.toarray()[0]

        def model_func(data):
            # Cache the samples generated from Shap
            global data_cache
            data_cache = data
            return np.zeros(data.shape[0])

        explainer = shap.KernelExplainer(model_func, np.zeros((1, numeric_test_data.shape[0])))
        explainer.shap_values(numeric_test_data)
        global data_cache
        kernelData = data_cache
        textData = vectorizer.inverse_transform(1 - kernelData)
        example = tokenize(evaluation_examples[0])
        filteredData = []
        for textDataPermuted in textData:
            filteredData.append(''.join(filter(lambda x: x not in textDataPermuted, example)))
        # Predict on original model
        prediction = model.predict(filteredData).tolist()
        module_logger.info("prediction from model: {}".format(str(prediction)))
        self.han_model.fine_tune_model(filteredData, prediction, epochs=epochs)
