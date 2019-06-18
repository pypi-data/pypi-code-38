"""Test compose commands."""
from click.testing import CliRunner

from megalus.compose.commands import restart, scale, up


def test_restart(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(restart, ['django'], obj=obj)
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
               '-f docker-compose.override.yml restart django'.format(service_path) in running_command


def test_scale(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(scale, ['django', '2'], obj=obj)
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
        assert 'cd {} && docker-compose -f docker-compose.yml -f ' \
               'docker-compose.override.yml up -d --scale django=2'.format(service_path) in running_command


def test_up_detached(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(up, ['-d', 'django'], obj=obj)
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
               '-f docker-compose.override.yml up -d --remove-orphans django'.format(service_path) in running_command


def test_up_multiple_services(caplog, obj, mocker, ngrok_response):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.compose.commands.requests.get', return_value=ngrok_response)
        result = runner.invoke(up, ['django', 'pyramid'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "django" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'django'
        ][0]
        assert 'cd {} && docker-compose -f docker-compose.yml ' \
               '-f docker-compose.override.yml up -d --remove-orphans django'.format(service_path) in running_command

        running_command = [
            message
            for message in caplog.messages
            if "pyramid" in message
        ][0]
        service_path = [
            service['working_dir']
            for service in obj.all_services
            if service['name'] == 'pyramid'
        ][0]
        assert 'cd {} && MEGALUS_NGROK_TEST_ENV=http://87f3557f.ngrok.io ' \
               'NGROK_DOMAIN=87f3557f.ngrok.io docker-compose -f ' \
               'docker-compose.yml up -d --remove-orphans pyramid'.format(service_path) in running_command


def test_up_service_with_ngrok(caplog, obj, mocker, ngrok_response):
    """Test Get Ngrok URL."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.compose.commands.requests.get', return_value=ngrok_response)
        result = runner.invoke(up, ['pyramid'], obj=obj)
        assert result.exit_code == 0
        running_command = [
            message
            for message in caplog.messages
            if "pyramid" in message
        ][0]
        assert "http://87f3557f.ngrok.io" in running_command
