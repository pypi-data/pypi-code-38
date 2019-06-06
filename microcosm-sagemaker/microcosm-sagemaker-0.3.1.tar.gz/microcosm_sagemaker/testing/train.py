import tempfile
from pathlib import Path
from typing import Mapping

from microcosm_sagemaker.commands import train
from microcosm_sagemaker.testing.bytes_extractor import ExtractorMatcherPair
from microcosm_sagemaker.testing.cli_test_case import CliTestCase
from microcosm_sagemaker.testing.directory_comparison import directory_comparison


class TrainCliTestCase(CliTestCase):
    """
    Helper base class for writing tests of the train cli.

    """
    input_data_path: Path
    gold_output_artifact_path: Path
    output_artifact_matchers: Mapping[Path, ExtractorMatcherPair]

    def test_train(self) -> None:
        """
        Runs the `train` command on the given `input_data_path` and then
        recursively checks the contents of the output artifact against the
        expected contents in `gold_output_artifact_path`.  It is also possible
        to leave certain files out of the gold dir, and instead specify a
        matcher that should be used for the contents of the given file instead.

        """
        with tempfile.TemporaryDirectory() as output_artifact_path:
            self.run_and_check(
                command_name="train",
                command=train.main,
                args=[
                    "--input-data",
                    str(self.input_data_path),
                    "--output-artifact",
                    output_artifact_path,
                ],
            )

            directory_comparison(
                gold_dir=self.gold_output_artifact_path,
                actual_dir=Path(output_artifact_path),
                matchers=self.output_artifact_matchers,
            )
