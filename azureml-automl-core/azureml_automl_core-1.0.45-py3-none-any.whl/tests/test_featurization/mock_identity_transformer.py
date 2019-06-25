from azureml.automl.core.featurizer.transformer import AutoMLTransformer
from azureml.automl.core.column_purpose_detection.types import StatsAndColumnPurposeType
from automl.client.core.common.types import DataSingleColumnInputType, DataInputType


class MockIdentityTransformer(AutoMLTransformer):
    def __init__(self, memory_estimate: int):
        super().__init__()
        self.memory_estimate = memory_estimate
        self.if_transform_called = False

    def fit(self, X: DataSingleColumnInputType, y: DataSingleColumnInputType = None) -> "MockIdentityTransformer":
        """
        Fit method.

        :param X: Input data.
        :param y: Labels.
        :return: self.
        """
        return self

    def transform(self, X: DataSingleColumnInputType) -> DataSingleColumnInputType:
        """
        Transform method.

        :param X: Input data.
        :return: Transformed data.
        """
        self.if_transform_called = True
        return X

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint by adding this featurizer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken in bytes.
        """
        # TODO Make this method abstract once we have all featurizers implementing this method.
        return self.memory_estimate
