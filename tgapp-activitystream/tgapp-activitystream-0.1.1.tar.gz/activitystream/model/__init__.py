# -*- coding: utf-8 -*-

#   from sqlalchemy.ext.declarative import declarative_base
import tg, logging
from tg import config
from tgext.pluggable import PluggableSession

TGAPP_NAME = 'tgapp-activitystream'

log = logging.getLogger(TGAPP_NAME)

DBSession = PluggableSession()

Action = None


def init_model(app_session):
    DBSession.configure(app_session)


def import_models():
    global Action
    use_sqlalchemy = config.get('use_sqlalchemy')
    if use_sqlalchemy:
        raise NotImplementedError("tgapp-activitystream is not implemented for sqlalchemy yet.")
        #   from .sqla_models import Registration
        pass
    else:
        from .ming_models import Action


class PluggableSproxProvider(object):
    def __init__(self):
        self._provider = None

    def _configure_provider(self):
        if tg.config.get('use_sqlalchemy'):
            log.info('Configuring %s for SQLAlchemy' % TGAPP_NAME)
            from sprox.sa.provider import SAORMProvider
            self._provider = SAORMProvider(session=DBSession)
        elif tg.config.get('use_ming'):
            log.info('Configuring %s for Ming' % TGAPP_NAME)
            from sprox.mg.provider import MingProvider
            self._provider = MingProvider(DBSession)
        else:
            raise ValueError('%s should be used with sqlalchemy or ming' % TGAPP_NAME)

    def __getattr__(self, item):
        if self._provider is None:
            self._configure_provider()

        return getattr(self._provider, item)

provider = PluggableSproxProvider()
