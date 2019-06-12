import os

class Development(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/potnanny.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    POTNANNY_PLUGIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../potnanny-plugins") )
    POTNANNY_LOG = "/tmp/potnanny.log"

class Production(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', "sqlite:////var/local/potnanny/potnanny.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    POTNANNY_PLUGIN_PATH = os.getenv('POTNANNY_PLUGIN_PATH', '/opt/potnanny/plugins')
    POTNANNY_LOG = "/var/log/potnanny/potnanny.log"

class Testing(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    POTNANNY_PLUGIN_PATH = Development.POTNANNY_PLUGIN_PATH
    POTNANNY_LOG = Development.POTNANNY_LOG
