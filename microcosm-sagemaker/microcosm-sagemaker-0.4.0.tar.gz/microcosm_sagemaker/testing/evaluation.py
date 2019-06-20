from abc import ABC
from pathlib import Path

from microcosm.loaders import load_each, load_from_dict

from microcosm_sagemaker.app_hooks import create_evaluate_app
from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.evaluation import Evaluation
from microcosm_sagemaker.input_data import InputData


class EvaluationTestCase(ABC):
    # These should be defined in actual test case derived class
    evaluation_name: str
    root_input_artifact_path: Path
    input_data_path: Path

    @property
    def extra_config(self) -> dict:
        """
        Derived classes can override this to provide extra config to the
        create_app function.

        """
        return {}

    # If necessary, this function can be overridden to do something more
    # sophisticated to check the evaluation
    def check_evaluation(
        self,
        bundle: Bundle,
        evaluation: Evaluation,
        input_data: InputData,
    ) -> None:
        evaluation(bundle, input_data)

    @property
    def _input_data(self) -> InputData:
        return InputData(self.input_data_path)

    def setup(self) -> None:
        self.graph = create_evaluate_app(
            extra_loader=load_each(
                load_from_dict(
                    active_evaluation=self.evaluation_name,
                    root_input_artifact_path=self.root_input_artifact_path,
                ),
                load_from_dict(self.extra_config),
            ),
        )

    def test_evaluation(self) -> None:
        self.check_evaluation(
            self.graph.active_bundle,
            self.graph.active_evaluation,
            self._input_data,
        )
