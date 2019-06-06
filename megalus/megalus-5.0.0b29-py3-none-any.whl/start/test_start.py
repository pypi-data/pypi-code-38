"""Test start command."""
from click.testing import CliRunner

from megalus.start.commands import start


def test_start_command(caplog, obj, mocker, ngrok_response):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.compose.commands.requests.get', return_value=ngrok_response)
        result = runner.invoke(start, ['api1', 'api2'], obj=obj)
        assert result.exit_code == 0

        # Test project 'api1'
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
        assert 'cd {} && docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d'.format(
            service_path) in running_command

        # Test project 'api2'
        running_command = [
            message
            for message in caplog.messages
            if "Running command:" in message
        ][-1]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'pyramid'
        ][0]
        assert 'cd {} && MEGALUS_NGROK_TEST_ENV=http://87f3557f.ngrok.io' \
               ' NGROK_DOMAIN=87f3557f.ngrok.io docker-compose -f ' \
               'docker-compose.yml up -d'.format(service_path) in running_command
