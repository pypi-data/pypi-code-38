from os.path import join, exists

from click.testing import CliRunner

from kudu.__main__ import cli
from kudu.config import write_config


def test_pull_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['pull', '-f', 519629])
        assert result.exit_code == 0
        assert exists(join('519629_1549718939', 'index.html'))
        assert exists(join('519629_1549718939', '519629_1549718939.png'))
        assert exists(join('519629_1549718939', 'folder', 'foobar.json'))


def test_pull_project():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write_config({'file_id': 519629})
        result = runner.invoke(cli, ['pull'])
        assert result.exit_code == 0
        assert exists('index.html')
        assert exists('thumbnail.png')
        assert exists(join('folder', 'foobar.json'))


def test_interface():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write_config({'file_id': 527702})
        result = runner.invoke(cli, ['pull'])
        assert result.exit_code == 0
        assert exists(join('interface', 'index.html'))
        assert exists(join('interface_1', 'index.html'))
        assert exists(join('lang', 'AR.csv'))
