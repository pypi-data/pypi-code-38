# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with the renset-152 model."""
from azureml.accel.models.accel_model import AccelModel


class AbstractResnet152(AccelModel):
    """Abstract baseclass for resnet 152."""

    _prefix = 'resnet_v1_152/'
    _save_name = "resnet152"

    classifier_input = '{0}pool5'.format(_prefix)
    classifier_output = '{0}predictions/Softmax:0'.format(_prefix)
    classifier_uri = "https://go.microsoft.com/fwlink/?linkid=2026005"

    def get_input_dims(self, index=0):
        """Get nth model input tensor dimensions."""
        return [None, 224, 224, 3]

    def get_output_dims(self, index=0):
        """Get nth model output tensor dimensions."""
        return [None, 1, 1, 2048]


class Resnet152(AbstractResnet152):
    """Float-32 Version of Resnet-152."""

    _modelname = "rn152"
    _modelver = "1.1.2"

    def __init__(self, model_base_path, is_frozen=False):
        """Create a Float-32 version of resnet 152.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the resnet-152 be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        """
        super().__init__(model_base_path, self._modelname, self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2018638", self._save_name, is_frozen=is_frozen)


class QuantizedResnet152(AbstractResnet152):
    """Quantized version of Renset-152."""

    _modelname = "msfprn152"
    _modelver = "1.1.3"

    def __init__(self, model_base_path, is_frozen=False, custom_weights_directory=None):
        """Create a version of resnet 50 quantized for the Azure ML Hardware Accelerated Models Service.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the resnet-152 be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        :param custom_weights_directory: Directory to load pretrained resnet-50 weights from. Can load weights from
        either a float-32 version or a quantized version. If none, will load weights trained for accuracy on the
        Imagenet dataset.
        """
        super().__init__(model_base_path,
                         self._modelname,
                         self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2025067",
                         self._save_name,
                         is_frozen=is_frozen,
                         weight_path=custom_weights_directory)
