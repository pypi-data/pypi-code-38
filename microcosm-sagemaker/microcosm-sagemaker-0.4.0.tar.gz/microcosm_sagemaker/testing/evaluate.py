from pathlib import Path

from microcosm_sagemaker.commands import evaluate
from microcosm_sagemaker.testing.cli_test_case import CliTestCase


class EvaluateCliTestCase(CliTestCase):
    """
    Helper base class for writing tests of the evaluate cli.

    """
    input_data_path: Path
    input_artifact_path: Path

    def test_evaluate(self) -> None:
        """
        Runs the `evaluate` command on the given `input_data_path` and
        `input_artifact_path`.
        """
        self.run_and_check(
            command_name="evaluate",
            command=evaluate.main,
            args=[
                "--input-data",
                str(self.input_data_path),
                "--input-artifact",
                str(self.input_artifact_path),
            ],
        )
