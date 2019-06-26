import logging

from flask_arango_orm import ArangoORM
from flask_marshmallow import Marshmallow
from quaerere_base_flask.views.base import LOGGER as qbf_v_b_logger

LOGGERS = ['quaerere_base_flask', 'quaerere_base_flask.views.base']

arangodb = ArangoORM()
marshmallow = Marshmallow()


def get_db():
    return arangodb.connection

def register_logging(app):
    logging.basicConfig(level=app.logger.level)
    qbf_v_b_logger.handlers = app.logger.handlers
    qbf_v_b_logger.setLevel(app.logger.level)
