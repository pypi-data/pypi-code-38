# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
import warnings
from unittest import TestCase

import sqlalchemy as sa
from sqlalchemy.exc import SAWarning

from rattail.config import make_config
from rattail.db import model
from rattail.db import Session


warnings.filterwarnings(
    'ignore',
    r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively\, "
    "and SQLAlchemy must convert from floating point - rounding errors and other "
    "issues may occur\. Please consider storing Decimal numbers as strings or "
    "integers on this platform for lossless storage\.$",
    SAWarning, r'^sqlalchemy\..*$')


class NullProgress(object):
    """
    Dummy progress bar which does nothing, but allows for better test coverage
    when used with code under test.
    """

    def __init__(self, message, count):
        pass

    def update(self, value):
        pass

    def destroy(self):
        pass


class RattailMixin(object):
    """
    Generic mixin for ``TestCase`` classes which need common Rattail setup
    functionality.
    """
    engine_url = os.environ.get('RATTAIL_TEST_ENGINE_URL', 'sqlite://')
    host_engine_url = os.environ.get('RATTAIL_TEST_HOST_ENGINE_URL')

    def postgresql(self):
        return self.config.rattail_engine.url.get_dialect().name == 'postgresql'

    def setUp(self):
        self.setup_rattail()

    def tearDown(self):
        self.teardown_rattail()

    def setup_rattail(self):
        config = self.make_rattail_config()
        self.config = config
        self.rattail_config = config

        engine = sa.create_engine(self.engine_url)
        config.rattail_engines['default'] = engine
        config.rattail_engine = engine

        if self.host_engine_url:
            config.rattail_engines['host'] = sa.create_engine(self.host_engine_url)

        model = self.get_rattail_model()
        model.Base.metadata.create_all(bind=engine)

        Session.configure(bind=engine, rattail_config=config)
        self.session = Session()

    def teardown_rattail(self):
        self.session.close()
        Session.configure(bind=None, rattail_config=None)
        model = self.get_rattail_model()
        model.Base.metadata.drop_all(bind=self.rattail_config.rattail_engine)

    def make_rattail_config(self, **kwargs):
        kwargs.setdefault('files', [])
        return make_config(**kwargs)

    def get_rattail_model(self):
        return model


class RattailTestCase(RattailMixin, TestCase):
    """
    Generic base class for Rattail tests.
    """


class DataTestCase(TestCase):

    engine_url = os.environ.get('RATTAIL_TEST_ENGINE_URL', 'sqlite://')

    def setUp(self):
        self.engine = sa.create_engine(self.engine_url)
        model.Base.metadata.create_all(bind=self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()
        self.extra_setup()

    def extra_setup(self):
        """
        Derivative classes may define this as necessary, to avoid having to
        override the :meth:`setUp()` method.
        """

    def tearDown(self):
        self.session.close()
        Session.configure(bind=None)
        model.Base.metadata.drop_all(bind=self.engine)
