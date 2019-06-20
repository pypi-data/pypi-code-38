import os

import redis

from worker.data.operations import is_number


class RedisMixin(object):
    def __init__(self, *args, **kwargs):
        pass

    def get_redis(self):
        if not getattr(self, 'redis', None):
            key = os.getenv('CACHE_URL', None)

            if not key:
                raise Exception('redis key (CACHE_URL) not found in Environment Variables.')

            self.redis = redis.Redis.from_url(key)

        return self.redis

    @staticmethod
    def get_redis_key(asset_id, app_name, module_name=None):
        key = "corva/{0}.{1}".format(app_name, asset_id)
        if module_name:
            key += ".{0}".format(module_name)

        return key


class LoggingMixin(object):

    LOGGING_LEVELS = [
        "all",  # lowest level
        "debug",
        "info",
        "warn",
        "error",
        "fatal",
        "off"
    ]

    def init_logging(self, *args, **kwargs):
        self.logging_level = os.getenv("LOGGING_LEVEL", "info").lower()
        self.logging_asset_id = os.getenv("LOGGING_ASSET_ID", 0)

        if self.logging_level not in self.LOGGING_LEVELS:
            self.logging_level = "off"

        if is_number(self.logging_asset_id):
            self.logging_asset_id = int(self.logging_asset_id)

    def all(self, asset_id, text):
        self.call('all', asset_id, text)

    def debug(self, asset_id, text):
        self.call('debug', asset_id, text)

    def info(self, asset_id, text):
        self.call('info', asset_id, text)

    def warn(self, asset_id, text):
        self.call('warn', asset_id, text)

    def error(self, asset_id, text):
        self.call('error', asset_id, text)

    def fatal(self, asset_id, text):
        self.call('fatal', asset_id, text)

    def off(self, asset_id, text):
        pass

    def call(self, method, asset_id, text):
        if str(method) in self.LOGGING_LEVELS[0:self.LOGGING_LEVELS.index(self.logging_level) + 1] \
                and asset_id == self.logging_asset_id:
            self.log(asset_id, text)

    @staticmethod
    def log(asset_id, text):
        print('asset_id_{} -> {}'.format(asset_id, text))


class RollbarMixin(object):
    def init_rollbar(self, *args, **kwargs):
        self.rollbar = kwargs.pop('rollbar', None)
        super().__init__(*args, **kwargs)

    def track_error(self, message: str, level: str):
        # Levels: critical, error, warning, info, debug, and ignored
        if not self.rollbar:
            return

        level = level.lower()

        self.rollbar.report_message(message, level)
