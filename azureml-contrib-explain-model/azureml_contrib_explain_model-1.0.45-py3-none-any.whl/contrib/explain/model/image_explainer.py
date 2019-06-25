# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the image explainer for getting model explanations from image data."""

import numpy as np
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from skimage.segmentation import slic

from .common.image_explainer_utils import _mask_image
from azureml.explain.model.common.base_explainer import LocalExplainer
from azureml.explain.model.common.blackbox_explainer import BlackBoxMixin
from azureml.explain.model.common.explanation_utils import _convert_to_list, _append_shap_values_instance, \
    _convert_single_instance_to_multi
from azureml.contrib.explain.model.explanation.explanation import _create_local_explanation
from azureml.explain.model._internal.constants import Attributes, ExplainParams, ExplainType

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap


class ImageExplainer(LocalExplainer, BlackBoxMixin):
    """Explain a model trained on an image dataset."""

    def __init__(self, model, size, is_function=False, **kwargs):
        """Initialize the Image Explainer.

        :param model: An object that represents a model. It is assumed that for the classification case
            it has a method of predict_proba() returning the prediction probabilities for each
            class and for the regression case a method of predict() returning the prediction value.
        :type model: object
        :param size: The size of the image.
        :type size: tuple(int)
        :param is_function: Default set to false, set to True if passing predict or predict_proba
            function instead of model.
        :type is_function: bool
        """
        super(ImageExplainer, self).__init__(model, is_function=is_function, **kwargs)
        self._logger.debug('Initializing ImageExplainer')
        self._size = size

    def _create_explainer(self, function, img_path, n_segments=50):
        """Segment the image and create the KernelExplainer to explain the superpixels.

        :param function: The function to call on the blackbox image model.
        :type function: function
        :param img_path: The image path.
        :type img_path: str
        :param n_segments: The number of segments or superpixels to automatically generate.
        :type n_segments: int
        :return: The constructed KernelExplainer.
        :rtype: shap.KernelExplainer
        """
        img = image.load_img(img_path, target_size=self._size)
        img_orig = image.img_to_array(img)
        # segment this image
        segments_slic = slic(img, n_segments=n_segments, compactness=30, sigma=3)

        def f(z):
            return function(preprocess_input(_mask_image(z, segments_slic, img_orig, 255)))

        return shap.KernelExplainer(f, np.zeros((1, n_segments)))

    def _explain_instance(self, explainer, img_path, n_segments=50, classes=None):
        """Explains the best example row with image data.

        :param explainer: The KernelExplainer used for image explanation.
        :type explainer: shap.KernelExplainer
        :param n_segments: The number of segments or superpixels to automatically generate.
        :type n_segments: int
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :return: The shap values for image superpixels.
        :rtype: numpy.ndarray
        """
        ns = max(600, n_segments, (0 if classes is None else len(classes)))
        # use Kernel SHAP to explain the network's predictions
        return explainer.shap_values(np.ones((1, n_segments)), nsamples=ns)

    def explain_local(self, evaluation_examples, n_segments=50, classes=None):
        """Explain a model locally by explaining its predictions on the image document.

        If multiple documents are passed, we choose the one with the highest predicted probability
        or confidence from the given evaluation examples.

        :param evaluation_examples: A list of image paths.
        :type evaluation_examples: list
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :return: A local explanation of the image containing the feature importance values for superpixels,
            expected values and the chosen golden image with highest confidence score in model.
        :rtype: LocalExplanation
        """
        features = list(range(n_segments))
        shap_values = None
        for image_example in evaluation_examples:
            explainer = self._create_explainer(self.function, image_example, n_segments)
            tmp_shap_values = self._explain_instance(explainer, image_example, n_segments, classes)
            if shap_values is None:
                shap_values = _convert_single_instance_to_multi(tmp_shap_values)
            else:
                shap_values = _append_shap_values_instance(shap_values, tmp_shap_values)
        shap_values = np.asarray(shap_values)
        # TODO: this would put the expected_value associated with last image's explainer
        # as the expected_values. Should we take an average instead?
        if explainer is not None and hasattr(explainer, Attributes.EXPECTED_VALUE):
            expected_values = explainer.expected_value
            if isinstance(expected_values, np.ndarray):
                expected_values = expected_values.tolist()
        local_importance_values = _convert_to_list(shap_values)
        kwargs = {ExplainParams.METHOD: ExplainType.SHAP}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        if self.predict_proba_flag:
            kwargs[ExplainType.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainType.MODEL_TASK] = ExplainType.REGRESSION
        if self.model is not None:
            kwargs[ExplainParams.MODEL_TYPE] = str(type(self.model))
        else:
            kwargs[ExplainParams.MODEL_TYPE] = ExplainType.FUNCTION
        return _create_local_explanation(local_importance_values=np.array(local_importance_values),
                                         expected_values=expected_values, image_explanation=True,
                                         features=features, **kwargs)
