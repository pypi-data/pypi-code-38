import os
from datetime import date, timedelta

import pytest
import phishme_intelligence.core.config_check
import phishme_intelligence.core.intelligence
import collections
import json
import io
import mock
import sys

from contextlib import contextmanager
from six.moves import configparser


Intelligence = collections.namedtuple('Intelligence', ['json', 'object'])


class NotMocked(Exception):
    def __init__(self, filename):
        super(NotMocked, self).__init__("The file %s was opened, but not mocked." % filename)
        self.filename = filename


class OpenMock(object):
    def __init__(self):
        self.files_opened = []

    def file_open_count(self, filename):
        return len([f for f in self.files_opened if f[0] is filename])

    def file_was_open(self, filename):
        return self.file_open_count(filename) > 0

    def file_was_open_with(self, filename, *args, **kwargs):
        print(args)
        print(kwargs)
        return len([f for f in self.files_opened if f[0] is filename and f[1] == args and f[2] == kwargs]) > 0

    @contextmanager
    def mock_open(self, filename, contents=None, exists=True, complain=True):
        """Mock the open() builtin function on a specific filename

        Let execution pass through to open() on files different than
        :filename:. Return a StringIO with :contents: if the file was
        matched. If the :contents: parameter is not given or if it is None,
        a StringIO instance simulating an empty file is returned.

        If :complain: is True (default), will raise an AssertionError if
        :filename: was not opened in the enclosed block. A NotMocked
        exception will be raised if open() was called with a file that was
        not mocked by mock_open.

        If :exists: is False, will raise an OSError to mock calling a
        nonexistant file.

        The majority of this function is from
        http://mapleoin.github.io/perma/mocking-python-file-open
        It's been modified to track files that were open along with
        the arguments passed to open.
        """
        open_files = set()

        def mock_file(*args, **kwargs):

            self.files_opened.append((args[0], args[1:], kwargs))
            if args[0] == filename:
                if not exists:
                    raise IOError('does not exist')
                if sys.version_info[0] == 2:
                    f = io.StringIO(contents.decode('utf-8'))
                else:
                    f = io.StringIO(contents)
                f.name = filename
            else:
                mocked_file.stop()
                f = open(*args, **kwargs)
                mocked_file.start()
            open_files.add(f.name)
            return f
        if sys.version_info[0] == 2:
            mocked_file = mock.patch('__builtin__.open', mock_file)
        else:
            mocked_file = mock.patch('builtins.open', mock_file)
        mocked_file.start()
        try:
            yield
        except NotMocked as e:
            if e.filename != filename:
                raise
        mocked_file.stop()
        try:
            open_files.remove(filename)
        except KeyError:
            if complain:
                raise AssertionError("The file %s was not opened." % filename)
        for f_name in open_files:
            if complain:
                raise NotMocked(f_name)


@pytest.fixture(scope="function")
def setup_config_ini():
    test_config = configparser.ConfigParser()
    config_ini = os.path.join(os.path.dirname(__file__), './config.ini')
    test_config.read(config_ini)

    yesterday = date.today() - timedelta(1)
    # If yesterday is a Saturday or Sunday (6 or 7) go back to Friday
    if yesterday.isoweekday() == 6:
        yesterday = yesterday - timedelta(1)
    if yesterday.isoweekday() == 7:
        yesterday = yesterday - timedelta(2)

    test_config.set('pm_api', 'init_date', yesterday.strftime('%Y-%m-%d'))

    return test_config


@pytest.fixture(scope="function")
def setup_phishme_intelligence(setup_config_ini, tmpdir_factory):
    return phishme_intelligence.core.phishme.PhishMeIntelligence(config=setup_config_ini,
                                                                 config_file_location=tmpdir_factory.mktemp('config_file'))


@pytest.fixture(scope='function')
def setup_config_check(setup_config_ini):
    phishme_intelligence.core.config_check.IS_VALID_CONFIG = True
    return phishme_intelligence.core.config_check.ConfigCheck(setup_config_ini)


@pytest.fixture(scope='function')
def load_json():
    """
    Fixture for loading JSON data for sample campaign
    """
    json_data_path = os.path.join(os.path.dirname(__file__), 'phishme_intelligence_data.json')
    with open(json_data_path) as json_data:
        test_malware_data = json.load(json_data)

    return test_malware_data


@pytest.fixture(scope='function')
def intel_data(load_json):
    """
    Fixture for creating test Intelligence data (no config.ini)
    """
    return Intelligence(json=load_json.get('data'),
                        object=phishme_intelligence.core.intelligence.Malware(load_json.get('data')))


@pytest.fixture(scope='function')
def intel_data_config(load_json, setup_config_ini):
    """
    Fixture for creating test Intelligence data with config.ini
    """
    setup_config_ini.set('pm_api', 'base_url', 'https://www.example.com/apiv1')
    return Intelligence(json=load_json.get('data'),
                        object=phishme_intelligence.core.intelligence.Malware(load_json.get('data'),
                                                                              config=setup_config_ini))


@pytest.fixture(scope='function')
def fake_open():
    return OpenMock()


@pytest.fixture(scope='function')
def threat_report_json():
    with open('%s/valid_response.json' % os.path.dirname(os.path.realpath(__file__))) as f:
        report_json = f.read()
    return report_json


@pytest.fixture(scope='function')
def individual_threat_json():
    with open('%s/individual_threat.json' % os.path.dirname(os.path.realpath(__file__))) as f:
        threat_json = f.read()
    return threat_json
