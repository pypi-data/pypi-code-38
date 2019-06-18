import datetime
import logging
import logging.handlers
import os
import re
import socket

from stackifyapm.conf.constants import LOG_PATH
from stackifyapm.utils import compat

__all__ = ("setup_logging", "Config")


class ConfigError(ValueError):
    def __init__(self, msg, field_name):
        self.field_name = field_name
        super(ValueError, self).__init__(msg)


class _ConfigValue(object):
    def __init__(self, dict_key, env_key=None, type=compat.text_type, validators=None, default=None, required=False):
        self.type = type
        self.dict_key = dict_key
        self.validators = validators
        self.default = default
        self.required = required

        self.env_key = env_key or "STACKIFY_APM_" + dict_key

    def __get__(self, instance, owner):
        return instance._values.get(self.dict_key, self.default) if instance else self.default

    def __set__(self, instance, value):
        value = self._validate(instance, value)
        instance._values[self.dict_key] = value or self.type(value)

    def _validate(self, instance, value):
        if value is None and self.required:
            raise ConfigError(
                "Configuration error: value for {} is required.".format(self.dict_key), self.dict_key
            )
        if self.validators and value is not None:
            for validator in self.validators:
                value = validator(value, self.dict_key)
        instance._errors.pop(self.dict_key, None)
        return value


class _BoolConfigValue(_ConfigValue):
    def __init__(self, dict_key, true_string="true", false_string="false", **kwargs):
        self.true_string = true_string
        self.false_string = false_string
        super(_BoolConfigValue, self).__init__(dict_key, **kwargs)

    def __set__(self, instance, value):
        if isinstance(value, compat.string_types):
            if value.lower() == self.true_string:
                value = True
            elif value.lower() == self.false_string:
                value = False
        instance._values[self.dict_key] = bool(value)


class RegexValidator(object):
    def __init__(self, regex, verbose_pattern=None):
        self.regex = regex
        self.verbose_pattern = verbose_pattern or regex

    def __call__(self, value, field_name):
        value = compat.text_type(value)
        match = re.match(self.regex, value)
        if match:
            return value
        raise ConfigError("{} does not match pattern {}".format(value, self.verbose_pattern), field_name)


class _ConfigBase(object):
    _NO_VALUE = object()

    def __init__(self, config_dict=None, env_dict=None, inline_dict=None):
        self._values = {}
        self._errors = {}
        if config_dict is None:
            config_dict = {}
        if env_dict is None:
            env_dict = os.environ
        if inline_dict is None:
            inline_dict = {}
        for field, config_value in self.__class__.__dict__.items():
            if not isinstance(config_value, _ConfigValue):
                continue

            new_value = self._NO_VALUE
            if config_value.env_key and config_value.env_key in env_dict:
                new_value = env_dict[config_value.env_key]
            elif field in inline_dict:
                new_value = inline_dict[field]
            elif config_value.dict_key in config_dict:
                new_value = config_dict[config_value.dict_key]

            if new_value is not self._NO_VALUE:
                try:
                    setattr(self, field, new_value)
                except ConfigError as e:
                    self._errors[e.field_name] = str(e)

    @property
    def errors(self):
        return self._errors


class Config(_ConfigBase):
    service_name = _ConfigValue("SERVICE_NAME", validators=[RegexValidator("^[a-zA-Z0-9 _-]+$")], required=True)
    environment = _ConfigValue("ENVIRONMENT", default='Production')
    hostname = _ConfigValue("HOSTNAME", default=socket.gethostname())
    capture_body = _ConfigValue("CAPTURE_BODY", default="off")
    async_mode = _BoolConfigValue("ASYNC_MODE", default=True)
    instrument_django_middleware = _BoolConfigValue("INSTRUMENT_DJANGO_MIDDLEWARE", default=True)
    service_version = _ConfigValue("SERVICE_VERSION")
    framework_name = _ConfigValue("FRAMEWORK_NAME", default=None)
    framework_version = _ConfigValue("FRAMEWORK_VERSION", default=None)
    instrument = _BoolConfigValue("DISABLE_INSTRUMENTATION", default=True)
    application_name = _ConfigValue("APPLICATION_NAME", default='Python Application')
    base_dir = _ConfigValue("BASE_DIR", default=None)
    config_file = _ConfigValue("CONFIG_FILE", default='stackify.json')


class IncrementalFileHandler(logging.handlers.RotatingFileHandler):
    """
    IncrementalFileHandler specific for Stackify Linux Agent
    """

    def __init__(self, filename, mode='a', maxBytes=0, encoding=None, delay=False):
        logging.handlers.RotatingFileHandler.__init__(
            self,
            filename=filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=0,
            encoding=encoding,
            delay=delay,
        )
        self.namer = None
        self.baseFilename = filename
        self.index = 0

    def doRollover(self):
        # close current stream
        if self.stream:
            self.stream.close()
            self.stream = None

        # increase the file index and generate new baseFilename
        self.index = self.index + 1
        self.baseFilename = self.rotation_filename("{}.{}".format(self.baseFilename, self.index))

        # set stream with the new file
        if not self.delay:
            self.stream = self._open()

        # Set stackify-python-apm increment log file to chmod 777
        os.chmod(self.baseFilename, 0o777)

    def rotation_filename(self, default_name):
        if not callable(self.namer):
            result = default_name
        else:
            result = self.namer(default_name)
        return result

    def emit(self, record):
        # recreate stream file if file was deleted
        if not os.path.exists(self.baseFilename):
            if not self.shouldRollover(record):
                if self.stream:
                    self.stream.close()
                self.stream = self._open()

        logging.handlers.RotatingFileHandler.emit(self, record)

        os.chmod(self.baseFilename, 0o777)


class StackifyFormatter(logging.Formatter):
    """
    StackifyFormatter specific for Stackify Windows Agent
    where it will force to show 6 digits for msecs
    """

    def formatTime(self, record, datefmt):
        return datetime.datetime.utcfromtimestamp(record.created).strftime(datefmt)


def setup_logging(client):
    """
    Configure loggings to pipe to Stackify Linux Agent
    """
    logger = None
    host_name = client.get_system_info().get("hostname")
    process_id = client.get_process_info().get("pid")
    filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

    def namer(name):
        num = int(name.split("/")[-1].split(".")[-1] or 0) + 1
        return "{}{}#{}-{}.log".format(LOG_PATH, host_name, process_id, num)

    try:
        handler = IncrementalFileHandler(filename, maxBytes=50000000)
        handler.setFormatter(StackifyFormatter("%(asctime)s> %(message)s", '%Y-%m-%d, %H:%M:%S.%f'))
        handler.setLevel(logging.DEBUG)
        handler.namer = namer

        logger = logging.getLogger("stackify_apm")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Set stackify-python-apm first log file to chmod 777
        os.chmod(filename, 0o777)

        for logger_name in ["stackifyapm", "stackifyapm.traces", "stackifyapm.errors"]:
            _logger = logging.getLogger(logger_name)
            _logger.setLevel(logging.DEBUG)

            if "error" in logger_name:
                _logger.addHandler(logging.FileHandler("{}{}.err".format(LOG_PATH, logger_name)))
            else:
                _logger.addHandler(logging.FileHandler("{}{}.out".format(LOG_PATH, logger_name)))
    except Exception:
        print("No such file or directory: '/usr/local/stackify/stackify-python-apm/log/'")

    return logger
