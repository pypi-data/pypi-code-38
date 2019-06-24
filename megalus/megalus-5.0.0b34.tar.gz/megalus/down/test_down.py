"""Test down command."""
from click.testing import CliRunner

from megalus.down.commands import down


def test_down_all_composes(caplog, obj, mocker, ngrok_response):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.compose.commands.requests.get', return_value=ngrok_response)
        result = runner.invoke(down, obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "api1" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'django'
        ][0]
        assert 'cd {} && docker-compose -f docker-compose.yml ' \
               '-f docker-compose.override.yml down'.format(service_path) in running_command

        running_command = [
            message
            for message in caplog.messages
            if "api2" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'pyramid'
        ][0]
        assert 'cd {} && MEGALUS_NGROK_TEST_ENV=http://87f3557f.ngrok.io ' \
               'NGROK_DOMAIN=87f3557f.ngrok.io docker-compose ' \
               '-f docker-compose.yml down'.format(service_path) in running_command


def test_down_with_remove(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(down, ['api1', '--remove-all'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "api1" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'django'
        ][0]
        assert 'cd {} && docker-compose -f docker-compose.yml ' \
               '-f docker-compose.override.yml down --rmi all --volumes ' \
               '--remove-orphans'.format(service_path) in running_command
