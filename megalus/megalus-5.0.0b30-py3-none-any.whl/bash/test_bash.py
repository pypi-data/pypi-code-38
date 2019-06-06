"""Test bash command."""
from click.testing import CliRunner

from megalus.bash.commands import bash


def test_bash_with_service(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.bash.commands.find_containers', return_value=[])
        result = runner.invoke(bash, ['django'], obj=obj)
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
        assert result.exit_code == 0
        assert 'cd {} && docker-compose -f docker-compose.yml -f docker-compose.override.yml ' \
               'run --rm --service-ports django /bin/bash'.format(service_path) in running_command


def test_bash_with_container(caplog, obj, mocker, django_container):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        mocker.patch('megalus.bash.commands.find_containers', return_value=[django_container])
        result = runner.invoke(bash, ['django'], obj=obj)
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
        assert result.exit_code == 0
        assert 'cd {} && docker exec -ti {} /bin/bash'.format(
            service_path, django_container.short_id) in running_command
