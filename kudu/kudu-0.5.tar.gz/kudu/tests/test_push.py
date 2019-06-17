import os

from click.testing import CliRunner

from kudu.__main__ import cli
from kudu.api import authenticate
from kudu.api import request as api_request


def test_push_zip():
    runner = CliRunner()
    with runner.isolated_filesystem():
        token = authenticate(os.environ['KUDU_USERNAME'], os.environ['KUDU_PASSWORD'])
        creation_time = api_request('get', '/files/%d/' % 519655, token=token).json()['creationTime']

        open('index.html', 'a').close()
        open('thumbnail.png', 'a').close()
        result = runner.invoke(cli, ['push', '-f', 519655])
        assert result.exit_code == 0

        result = runner.invoke(cli, ['pull', '-f', 519655])
        assert result.exit_code == 0
        assert os.path.exists(os.path.join('519655_1549795523377', 'index.html'))
        assert os.path.exists(os.path.join('519655_1549795523377', '519655_1549795523377.png'))
        assert creation_time != api_request('get', '/files/%d/' % 519655, token=token).json()['creationTime']


def test_push_json():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['push', '-f', 519631])
        assert result.exit_code == 2
