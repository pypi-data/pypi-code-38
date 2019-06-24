"""Test run command."""
from click.testing import CliRunner

from megalus.run.commands import run


def test_update_script(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(run, ['update'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][0]
        assert 'make update' in running_command
