# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class used for backward comptibility."""
import sys
import importlib


class ModuleNamespaceBackward:
    def __init__(self, module: str, new_namespace: str, old_namespace: str):
        self.module = module
        self.new_namespace = new_namespace
        self.old_namespace = old_namespace

    def backward_compatible_import_module(self) -> None:
        """Import the module and change the module name in sys to the old name."""
        try:
            loaded_module = importlib.import_module(".".join([self.new_namespace, self.module]))
            sys.modules[".".join([self.old_namespace, self.module])] = loaded_module
        except Exception as e:
            print("Import failure when loading packages due to {}, "
                  "prediction on models trained on new models might fail".format(e))

    def is_azureml_automl_core_namespace(self) -> bool:
        """Determine if this package currently belongs to azureml.automl.core."""
        return self.new_namespace.startswith("azureml.automl.core")

    def is_azureml_train_automl_namespace(self) -> bool:
        """Determine if this package currently belongs to azureml.train.automl."""
        return self.new_namespace.startswith("azureml.train.automl")


class BackwardCompatibleConstant:
    AZUREML_TRAIN_AUTOML_VENDOR = "azureml.train.automl._vendor.automl.client.core.common"
    AZUREML_AUTOML_CORE_COMMON_VENDOR = "azureml.automl.core._vendor.automl.client.core.common"
    AZUREML_AUTOML_CORE = "azureml.automl.core"
    AUTOML_CLIENT_CORE_COMMON = "automl.client.core.common"
    AZUREML_AUTOML_CORE_FEATURIZATION = "azureml.automl.core.featurization"
    AUTOML_CLIENT_CORE_COMMON_FEATURIZATION = "automl.client.core.common.featurization"
    MODULE_MODEL_WRAPPERS = "model_wrappers"
    MODULE_FEATURIZATION = "featurization"
    MODULE_DOWNLOADER = "_downloader"
    MODULE_EXPERIMENT_OBSERVER = "_experiment_observer"
    MODULE_ENGINEERED_FEATURE_NAMES = "_engineered_feature_names"
    MODULE_STATS_COMPUTATION = "stats_computation"
    MODULE_COLUMN_PURPOSE_DETECTION = "column_purpose_detection"
    MODULE_FEATURIZER = "featurizer"
    MODULE_DATA_TRANSFORMER = "data_transformer"


PackageMappings = {
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_MODEL_WRAPPERS,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE_COMMON_VENDOR,
                            BackwardCompatibleConstant.AZUREML_TRAIN_AUTOML_VENDOR),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_FEATURIZATION,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_DOWNLOADER,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_EXPERIMENT_OBSERVER,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_ENGINEERED_FEATURE_NAMES,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_STATS_COMPUTATION,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_COLUMN_PURPOSE_DETECTION,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_FEATURIZER,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON),
    ModuleNamespaceBackward(BackwardCompatibleConstant.MODULE_DATA_TRANSFORMER,
                            BackwardCompatibleConstant.AZUREML_AUTOML_CORE_FEATURIZATION,
                            BackwardCompatibleConstant.AUTOML_CLIENT_CORE_COMMON_FEATURIZATION),
}
