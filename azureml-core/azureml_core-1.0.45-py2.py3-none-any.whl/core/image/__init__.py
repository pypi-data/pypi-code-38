# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package is used for managing the Images you create with Azure Machine Learning service.

These Images are used to deploy a user's :class:`azureml.core.model.Model` as a Webservice. Images contain a Model,
execution script, and any dependencies needed for Model deployment. This Images package
has multiple subclasses such as ContainerImage for Docker Images, as well as preview
Images like FPGA.

To see an example of how you can use the :class:`azureml.core.image.container.ContainerImage`
class to create an Image and deploy a Webservice, follow the tutorial here:
https://docs.microsoft.com/en-us/azure/machine-learning/service/tutorial-deploy-models-with-aml#deploy-in-container-instances
"""

from azureml._base_sdk_common import __version__ as VERSION
from .image import Image
from .container import ContainerImage
from .unknown_image import UnknownImage


__version__ = VERSION

__all__ = [
    'Image',
    'ContainerImage',
    'UnknownImage'
]
