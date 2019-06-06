import logging
import sys
from traceback import print_exception
from typing import Iterable

import click
from click.testing import CliRunner
from hamcrest import assert_that, equal_to, is_


class CliTestCase:
    def setup(self) -> None:
        self.runner = CliRunner()

    def run_and_check(
        self,
        command_name: str,
        command: click.Command,
        args: Iterable[str],
    ) -> None:
        logging.info(f"Running command: {command_name} {' '.join(args)}")

        result = self.runner.invoke(command, args)

        if result.exit_code != 0:
            sys.stdout.write(result.output)
            if result.exc_info is not None:
                print_exception(*result.exc_info)

        assert_that(result.exit_code, is_(equal_to(0)))
