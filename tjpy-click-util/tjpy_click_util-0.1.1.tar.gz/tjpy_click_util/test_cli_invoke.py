import logging
from typing import Any, List

from click.testing import CliRunner, Result

_logger = logging.getLogger(__name__)


def invoke_cli(args: List[str],
               root_command: Any,
               *,
               verify_successful=True,
               always_log_output=True):
    runner = CliRunner()
    result: Result = runner.invoke(root_command, args, catch_exceptions=False)

    if verify_successful:
        if result.exit_code != 0:
            _logger.info("cli call output (on next line):\n" + str(result.output))
        assert result.exit_code == 0
    if always_log_output:
        _logger.info("cli call output (on next line):\n" + str(result.output))
    return result
