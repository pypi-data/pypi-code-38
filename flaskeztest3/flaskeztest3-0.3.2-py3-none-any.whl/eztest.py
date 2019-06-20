import threading
import warnings
from unittest import TextTestRunner, makeSuite
import json
import tempfile
import os
from importlib import import_module
import inspect

from flask_sqlalchemy import SQLAlchemy

import capybara

from .helpers import parse_module_name_from_filepath, convert_sql_table_to_sqlite_table
from .exceptions import FixtureDoesNotExistError


class EZTest(object):
    """Primary object for flaskeztest package."""

    def __init__(self):
        self.app = None
        self.db = None
        self.driver = None
        self.model_clases = None
        self.config = dict()
        self.testsuites = list()
        self.reflecting_schema = None
        self.sqlite_db_file = None
        self.sqlite_db_fn = None
        self.testsuites_package = None
        self.fixtures_dir = None

    def init_with_app_and_db(self, app, db):
        self.app = app
        self.db = db
        capybara.default_driver = "selenium"
        capybara.app = self.app
        capybara.ignore_hidden_elements = False

        self.clean_sqlalchemy_config()

        warnings.filterwarnings("ignore", message="Selenium support for PhantomJS has been deprecated, "
                                                  "please use headless versions of Chrome or Firefox instead")

        config_module_name = self.app.config.get('EZTEST_CONFIG_MODULE')
        config_module = import_module(parse_module_name_from_filepath(config_module_name))

        for (name, obj) in inspect.getmembers(config_module):
            if not inspect.isbuiltin(obj) and name.startswith('EZTEST'):
                self.config[name] = obj

        if self.config.get('EZTEST_REFLECTION_DB_URI'):
            self.reflecting_schema = True
            reflection_db_uri = self.config.get('EZTEST_REFLECTION_DB_URI')
            self.app.config['SQLALCHEMY_DATABASE_URI'] = reflection_db_uri
            reflection_db = SQLAlchemy(self.app)
            with self.app.app_context():
                self.db.Model.metadata.reflect(reflection_db.engine)
            self.model_clases = self.db.Model.metadata.tables
            for (_, table) in list(self.model_clases.items()):
                convert_sql_table_to_sqlite_table(table)
        else:
            self.reflecting_schema = False
            # Create dict with values being model class name and their values being the class itself
            model_class_objs = self.db.Model.__subclasses__()
            self.model_clases = dict([(obj.__name__, obj) for obj in model_class_objs])

        self.init_db_file()

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.sqlite_db_fn

        self.testsuites_package = self.config.get('EZTEST_SUITES_PACKAGE')
        self.fixtures_dir = self.config.get('EZTEST_FIXTURES_DIR')

        self.collect_testsuites()

        # So that we can use url_for before the app starts
        self.app.config['SERVER_NAME'] = 'localhost:5000'

        self.db.init_app(self.app)

    def run(self, suite_name=None, testcase_name=None):

        def run_app(app):
            from werkzeug.serving import run_simple
            run_simple('127.0.0.1', 5000, app)

        app_thread = threading.Thread(target=run_app, args=(self.app, ))
        app_thread.setDaemon(True)
        app_thread.start()

        runner = TextTestRunner()

        for suite in self.testsuites:
            if suite_name is None or suite.name == suite_name:

                if testcase_name is not None:
                    testcase = self.get_runnable_testcase_with_name_from_suite(testcase_name, suite)
                    if testcase is None:
                        return
                    print(("Running testcase %s.%s" % (suite_name, testcase_name)))
                    runner.run(testcase)
                    break
                else:
                    suite.init_test_instances(self)
                    runner.run(suite)

        self.remove_db_file()
        # Note when we come out of this function the main thread must call sys.exit(0) for flask app to stop running

    # These 3 are used by EZTestSuite before and after running tests

    def init_db_file(self):
        self.sqlite_db_file, self.sqlite_db_fn = tempfile.mkstemp()

    def remove_db_file(self):
        os.remove(self.sqlite_db_fn)

    # Used by EZTestSuite objects to load fixtures

    def load_fixture(self, fixture):
        """Seed DB with data in fixture json file and then return the testids also parsed from the file as dict."""

        models = self.parse_model_dicts_from_fixture(fixture)

        expected_models = dict()

        with self.app.app_context():
            for model in models:
                if 'row' in model:  # Otherwise we would find 'rows' key
                    expected_models[model['model']] = model['row']
                    self.seed_db_with_row_dict(model['model'], model['row'])
                else:
                    expected_models[model['model']] = list()
                    for row in model['rows']:
                        expected_models[model['model']].append(row)
                        self.seed_db_with_row_dict(model['model'], row)
            self.db.session.commit()

        return expected_models

    # Used by EZTestCase objects to reset data in between test cases
    def reset_db(self):
        with self.app.app_context():
            self.db.drop_all()
            self.db.create_all()
    # Private helpers

    def clean_sqlalchemy_config(self):

        for key in self.app.config.copy():
            if key.startswith('SQLALCHEMY'):
                self.app.config.pop(key)

        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def parse_model_dicts_from_fixture(self, fixture):
        try:
            return json.loads(open('%s/%s' % (self.fixtures_dir, fixture+'.json')).read())
        except (OSError, IOError):
            raise FixtureDoesNotExistError(self.fixtures_dir, fixture+'.json')

    def collect_testsuites(self):
        package_name = parse_module_name_from_filepath(self.testsuites_package)
        testsuites_init_module = import_module(package_name)
        suite_modules = testsuites_init_module.suite_modules
        for mod_name in suite_modules:
            module = import_module('%s.%s' % (package_name, mod_name))
            self.testsuites.append(module.suite)

    def seed_db_with_row_dict(self, model_name, row):
        if self.reflecting_schema:
            model_tab = self.model_clases[model_name]
            q = model_tab.insert().values(**row)
            self.db.engine.execute(q)
        else:
            self.db.session.add(self.model_clases[model_name](**row))

    def get_runnable_testcase_with_name_from_suite(self, name, suite):
        for tc_class in suite.test_classes:
            if tc_class.__name__ == name:
                return tc_class(self)
