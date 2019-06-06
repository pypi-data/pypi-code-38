"""test stop command."""
from click.testing import CliRunner

from megalus.stop.commands import stop


def test_stop_service(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(stop, ['django'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][-1]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'django'
        ][0]
        assert 'cd {} && docker-compose -f docker-compose.yml ' \
               '-f docker-compose.override.yml stop django'.format(service_path) in running_command


def test_stop_all(caplog, obj, mocker, ngrok_response):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.compose.commands.requests.get', return_value=ngrok_response)
        result = runner.invoke(stop, obj=obj)
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
        assert 'cd {} && docker-compose -f docker-compose.yml -f docker-compose.override.yml stop'.format(
            service_path) in running_command
        running_command = [
            message
            for message in caplog.messages
            if "api2" in message
        ][-1]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'pyramid'
        ][0]
        assert 'cd {} && MEGALUS_NGROK_TEST_ENV=http://87f3557f.ngrok.io ' \
               'NGROK_DOMAIN=87f3557f.ngrok.io docker-compose -f ' \
               'docker-compose.yml stop'.format(service_path) in running_command
