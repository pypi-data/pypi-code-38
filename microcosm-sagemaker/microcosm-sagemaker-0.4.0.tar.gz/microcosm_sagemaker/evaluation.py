from abc import ABC, abstractmethod

from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.input_data import InputData


class Evaluation(ABC):
    @abstractmethod
    def __call__(self, bundle: Bundle, input_data: InputData):
        pass
