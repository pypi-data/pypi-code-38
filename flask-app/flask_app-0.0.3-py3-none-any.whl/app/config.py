import os
from posix import environ


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "{{app_name}}")
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    SQLALCHEMY_BINDS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_DEV_URL")


class TestingConfig(BaseConfig):
    """Testing configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class StagingConfig(ProductionConfig):
    DEBUG = True


app_env = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig
}
