"""Test build command."""
from click.testing import CliRunner

from megalus.buildcmd.commands import build


def test_build(caplog, obj, mocker):
    runner = CliRunner()
    with runner.isolated_filesystem():
        mocker.patch('megalus.main.console.run')
        result = runner.invoke(build, ['django'], obj=obj)
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
        assert 'cd {} && docker-compose -f docker-compose.yml ' \
               '-f docker-compose.override.yml build --force-rm django ' \
               '| pv -lft -D 2 >> /temp/log'.format(service_path) in running_command
