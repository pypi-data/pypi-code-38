# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with the ssd-vgg model."""
from azureml.accel.models.accel_model import AccelModel


class AbstractSsdVgg(AccelModel):
    """Abstract baseclass for SSD-VGG."""

    _prefix = 'ssd_300_vgg/'
    _save_name = "ssd_vgg"

    _output_names = [
        'ssd_300_vgg/block4_box/Reshape_1:0',
        'ssd_300_vgg/block7_box/Reshape_1:0',
        'ssd_300_vgg/block8_box/Reshape_1:0',
        'ssd_300_vgg/block9_box/Reshape_1:0',
        'ssd_300_vgg/block10_box/Reshape_1:0',
        'ssd_300_vgg/block11_box/Reshape_1:0',
        'ssd_300_vgg/block4_box/Reshape:0',
        'ssd_300_vgg/block7_box/Reshape:0',
        'ssd_300_vgg/block8_box/Reshape:0',
        'ssd_300_vgg/block9_box/Reshape:0',
        'ssd_300_vgg/block10_box/Reshape:0',
        'ssd_300_vgg/block11_box/Reshape:0'
    ]

    _output_shapes = [
        [None, 37, 37, 4, 21],
        [None, 19, 19, 6, 21],
        [None, 10, 10, 6, 21],
        [None, 5, 5, 6, 21],
        [None, 3, 3, 4, 21],
        [None, 1, 1, 4, 21],
        [None, 37, 37, 4, 4],
        [None, 19, 19, 6, 4],
        [None, 10, 10, 6, 4],
        [None, 5, 5, 6, 4],
        [None, 3, 3, 4, 4],
        [None, 1, 1, 4, 4],
    ]

    def get_input_dims(self, index=0):
        """Get nth model input tensor dimensions."""
        return [None, 300, 300, 3]

    def get_output_dims(self, index=0):
        """Get nth model output tensor dimensions."""
        return self._output_shapes[index]


class SsdVgg(AbstractSsdVgg):
    """
    Float-32 Version of SSD-VGG.

    This model is in RGB format.
    """

    _modelname = "vggssd"
    _modelver = "1.1.3"

    def __init__(self, model_base_path, is_frozen=False):
        """Create a Float-32 version of SSD-VGG.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the model be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        """
        super().__init__(model_base_path, self._modelname, self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2086501",
                         self._save_name, is_frozen=is_frozen)

        # override default from AccelModel class
        self._output_tensor_list = self._output_names


class QuantizedSsdVgg(AbstractSsdVgg):
    """
    Quantized version of SSD-VGG.

    This model is in RGB format.
    """

    _modelname = "msfpvggssd"
    _modelver = "1.1.3"

    def __init__(self, model_base_path, is_frozen=False, custom_weights_directory=None):
        """Create a version of SSD VGG quantized for the Azure ML Hardware Accelerated Models Service.

        This model is in RGB format.
        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the model be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        :param custom_weights_directory: Directory to load pretrained weights from. Can load weights from
        either a float-32 version or a quantized version. If none, will load default weights.
        """
        super().__init__(model_base_path,
                         self._modelname,
                         self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2086713",
                         self._save_name,
                         is_frozen=is_frozen,
                         weight_path=custom_weights_directory)

        # override default from AccelModel class
        self._output_tensor_list = self._output_names
