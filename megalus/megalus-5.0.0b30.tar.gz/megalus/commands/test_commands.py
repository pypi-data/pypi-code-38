"""Test commands."""
from click.testing import CliRunner

from megalus.commands.commands import config, install


def test_default_config(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(config, obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][0]
        assert 'code ./megalus.yml' in running_command


def test_default_install(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(install, obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'django'
        ][0]
        assert 'make install' in running_command


def test_config_service(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(config, ['django'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][0]
        assert 'python ./api1/manage.py shell' in running_command
