import os
import shutil
import tempfile
import time
from os import mkdir, getcwd

from click.testing import CliRunner
from watchdog import events

from kudu.commands import link


def test_interface_path_converter():
    dst = os.path.join(tempfile.gettempdir(), str(time.time()))
    mkdir(dst)

    runner = CliRunner()
    with runner.isolated_filesystem():
        src = getcwd()

        mkdir('interface')
        open(os.path.join('interface', 'test.html'), 'wb').close()

        link.copyfiles(src, dst, link.InterfacePathConverter({'filename': 'interface_xy.zip'}))
        assert os.path.exists(os.path.join(dst, 'interface_xy', 'test.html'))

    shutil.rmtree(dst)


def test_presentation_path_converter():
    dst = os.path.join(tempfile.gettempdir(), str(time.time()))
    mkdir(dst)

    runner = CliRunner()
    with runner.isolated_filesystem():
        src = getcwd()

        open('index.html', 'wb').close()
        open('thumbnail.png', 'wb').close()
        mkdir('iPadOnly')
        open(os.path.join('iPadOnly', 'iPad.html'), 'wb').close()

        link.copyfiles(src, dst, link.PresentationPathConverter({'filename': '1234_4321.zip'}))
        assert os.path.exists(os.path.join(dst, 'slides', '1234_4321', 'index.html'))
        assert os.path.exists(os.path.join(dst, 'slides', '1234_4321', '1234_4321.png'))
        assert os.path.exists(os.path.join(dst, 'slides', '1234_4321', 'iPad.html'))

    shutil.rmtree(dst)


def test_copy_files_event_handler():
    dst = os.path.join(tempfile.gettempdir(), str(time.time()))
    mkdir(dst)

    runner = CliRunner()
    with runner.isolated_filesystem():
        src = getcwd()
        converter = link.PresentationPathConverter({'filename': '1234_4321.zip'})
        event_handler = link.CopyFilesEventHandler(src, dst, converter)

        class TestEvent(object):
            event_type = events.EVENT_TYPE_MODIFIED
            src_path = os.path.join(src, 'index.html')
            is_directory = False

        open('index.html', 'wb').close()
        event_handler.on_any_event(TestEvent)

        assert os.path.exists(os.path.join(dst, 'slides', '1234_4321', 'index.html'))

    shutil.rmtree(dst)
