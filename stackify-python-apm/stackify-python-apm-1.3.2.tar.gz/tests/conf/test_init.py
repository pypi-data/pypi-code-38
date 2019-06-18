import logging
import os
import re
from stat import ST_MODE
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.conf import Config
from stackifyapm.conf import ConfigError
from stackifyapm.conf import IncrementalFileHandler
from stackifyapm.conf import RegexValidator
from stackifyapm.conf import setup_logging
from stackifyapm.conf import StackifyFormatter
from stackifyapm.conf.constants import LOG_PATH


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "ASYNC_MODE": False,
    "CONFIG_FILE": 'path/to/stackify.json'
}


class RegexValidatorTest(TestCase):

    def test_should_return_correct_value(self):
        regex = "^[a-zA-Z0-9 _-]+$"
        value = 'some_value'
        _validate = RegexValidator(regex)

        validated_value = _validate(value, 'SOME_KEY')

        assert validated_value == value

    def test_should_raise_exception(self):
        regex = "^[a-zA-Z0-9 _-]+$"
        value = '#$%^'
        _validate = RegexValidator(regex)

        with self.assertRaises(ConfigError) as context:
            _validate(value, 'SOME_KEY')

        assert 'does not match pattern' in context.exception.args[0]


class ConfigTest(TestCase):

    def test_config_creation(sself):
        config = Config(CONFIG)

        assert config.environment == CONFIG["ENVIRONMENT"]
        assert config.hostname == CONFIG["HOSTNAME"]
        assert config.framework_name == CONFIG["FRAMEWORK_NAME"]
        assert config.framework_version == CONFIG["FRAMEWORK_VERSION"]
        assert config.application_name == CONFIG["APPLICATION_NAME"]
        assert config.config_file == CONFIG["CONFIG_FILE"]
        assert config.base_dir == CONFIG["BASE_DIR"]
        assert config.async_mode is False

    def test_default_config(self):
        config = Config()

        assert config.application_name == 'Python Application'
        assert config.environment == 'Production'
        assert config.config_file == 'stackify.json'
        assert config.framework_name is None
        assert config.framework_version is None
        assert config.base_dir is None
        assert config.async_mode is True


class IncrementalFileHandlerTest(TestCase):

    def setUp(self):
        self.filename = 'somefile.log'
        self.filename1 = self.filename + '.1'

        self.remove_file(self.filename)
        self.remove_file(self.filename1)

    def tearDown(self):
        self.remove_file(self.filename)
        self.remove_file(self.filename1)

    def remove_file(self, filename):
        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            pass

    def test_file_should_be_created(self):
        IncrementalFileHandler(self.filename, maxBytes=100)

        assert os.path.exists(self.filename)
        assert os.path.getsize(self.filename) == 0

    def test_should_log(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=100))

        logger.debug('some data to log')

        assert not os.path.getsize(self.filename) == 0

    def test_should_rotate(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=20))

        logger.debug('some data to log')  # size 17
        logger.debug('some data to log')  # size will go over 20 bytes and will create new file .1

        assert os.path.exists(self.filename)
        assert os.path.exists(self.filename1)

    def test_should_recreate_log_file_if_deleted(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=100))

        # making sure the log file was created
        logger.debug('some data to log')
        assert os.path.exists(self.filename)

        # we cant delete file if still in use
        if not os.name == 'nt':
            # making sure the log file was delete
            self.remove_file(self.filename)
            assert not os.path.exists(self.filename)

        logger.debug('some data to log')
        assert os.path.exists(self.filename)


class SetupLoggingTest(TestCase):

    def test_log_file_should_be_created(self):
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        setup_logging(client)

        assert os.path.exists(filename)

        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass

    def test_should_log_777_permission(self):
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        setup_logging(client)

        assert oct(os.stat(filename)[ST_MODE])[-3:] == '777'

    def test_if_file_remove_log_777_permission_(self):
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        logger = setup_logging(client)

        assert os.path.exists(filename)

        try:
            os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass

        logger.debug("Test")
        assert oct(os.stat(filename)[ST_MODE])[-3:] == '777'

    def test_log_timestamp_format(self):

        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        logger = setup_logging(client)

        assert os.path.exists(filename)

        logger.debug("Test")

        file = open(filename, "r")
        log_line = file.read()
        assert re.findall("\\d{4}-\\d{2}-\\d{2}, \\d{2}:\\d{2}:\\d{2}.\\d{6}> ", log_line)


class StackifyMsecFormatTest(TestCase):

    def test_should_msec_format(self):
        record = logging.makeLogRecord({'mgs': 'message'})
        datefmt = '%Y-%m-%d, %H:%M:%S.%f'
        stackify_formatter = StackifyFormatter()

        time_format = stackify_formatter.formatTime(record, datefmt)

        assert re.findall("\\d{4}-\\d{2}-\\d{2}, \\d{2}:\\d{2}:\\d{2}.\\d{6}", time_format)
