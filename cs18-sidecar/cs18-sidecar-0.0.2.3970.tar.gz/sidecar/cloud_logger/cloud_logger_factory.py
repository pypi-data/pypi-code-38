import importlib
import pkgutil
from inspect import getmembers, isclass, isabstract
from logging import Logger

from sidecar.aws_session import AwsSession
from sidecar.cloud_logger.file_logger import ICloudLogger
from sidecar.model.objects import ISidecarConfiguration
from .. import cloud_logger
from . import FileLogger


class CloudLoggerFactory(object):
    def __init__(self, config: ISidecarConfiguration, logger: Logger, logger_session: AwsSession, file_logger: FileLogger):
        self.config = config
        self.logger = logger
        self.cloud_logger = None
        self.logger_session = logger_session
        self.file_logger = file_logger

        for path, pkg_name, is_package in pkgutil.iter_modules(cloud_logger.__path__):
            if is_package and pkg_name == config.provider:
                pkg = importlib.import_module(".{}".format(pkg_name), package=cloud_logger.__name__)
                classes = getmembers(pkg, lambda m: isclass(m) and not isabstract(m) and issubclass(m, ICloudLogger))
                if len(classes) > 0:
                    self.cloud_logger = classes[0][1]
                break

    def create_instance(self):
        if self.cloud_logger is not None:
            return self.cloud_logger(self.config, self.logger, self.logger_session, self.file_logger)
        else:
            return self.file_logger
