# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Subclass of Image for when actual known Images are not imported."""
from .image import Image
from azureml._model_management._constants import UNKNOWN_IMAGE_TYPE, UNKNOWN_IMAGE_FLAVOR


class UnknownImage(Image):
    """UnknownImage class.

    This class is used for handling the scenarios where the SDK doesn't know the type of image but needs implemented
    functions (Image.list).
    """

    _image_type = UNKNOWN_IMAGE_TYPE
    _image_flavor = UNKNOWN_IMAGE_FLAVOR
    # _expected_payload_keys is inherited from the parent class Image

    def _initialize(self, workspace, obj_dict):
        """Initialize the UnknownImage object.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        :raises: None
        """
        super(UnknownImage, self)._initialize(workspace, obj_dict)
        self.image_flavor = UnknownImage._image_flavor

    @staticmethod
    def image_configuration():
        """Cannot return image configuration since image type is unknown.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Cannot create image configuration because specific Image type not imported. \
                                  ie. ContainerImage, AccelContainerImage, IotContainerImage")

    def run(self):
        """Test an image locally. This does not apply to unknown image types.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Cannot run image locally because specific Image type not imported. \
                                  ie. ContainerImage, IotContainerImage (AccelContainerImage cannot be run locally)")
