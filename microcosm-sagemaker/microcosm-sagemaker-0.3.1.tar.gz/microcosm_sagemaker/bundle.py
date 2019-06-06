from abc import ABC, abstractmethod
from typing import Callable, List

from microcosm_sagemaker.artifact import BundleInputArtifact, BundleOutputArtifact
from microcosm_sagemaker.input_data import InputData


class Bundle(ABC):
    """
    Abstract base class for all bundles.

    """
    predict: Callable

    @property
    @abstractmethod
    def dependencies(self) -> List["Bundle"]:
        """
        List of bundles upon which this bundle depends.  Whenever the `fit`,
        `save` or `load` methods are called on this bundle, it is guaranteed
        that the corresponding methods will have first been called all all
        `dependency` bundles.

        """
        ...

    @abstractmethod
    def fit(self, input_data: InputData) -> None:
        """
        Perform training

        """
        ...

    @abstractmethod
    def save(self, output_artifact: BundleOutputArtifact) -> None:
        """
        Save the trained model

        """
        ...

    @abstractmethod
    def load(self, input_artifact: BundleInputArtifact) -> None:
        """
        Load the trained model

        """
        ...
