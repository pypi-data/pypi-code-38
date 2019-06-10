# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Accelerate deep neural networks on FPGAs with the Azure ML Hardware Accelerated Models Service."""
from ._accel_container_image import AccelImageConfiguration, AccelContainerImage
from ._accel_onnx_converter import AccelOnnxConverter
from ._client import PredictionClient, client_from_service
from azureml.core import VERSION
from._accel_inference_config import AccelInferenceConfig

__version__ = VERSION

__all__ = [
    "AccelImageConfiguration",
    "AccelContainerImage",
    "AccelOnnxConverter",
    "PredictionClient",
    "client_from_service",
    "AccelInferenceConfig"
]
