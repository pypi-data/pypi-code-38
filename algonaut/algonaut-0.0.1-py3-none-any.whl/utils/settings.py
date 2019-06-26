from contextlib import contextmanager
import importlib
import logging
import yaml
import json
import sys
import os

from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from collections import defaultdict
from .celery import make_celery

logger = logging.getLogger(__name__)

class Settings(object):

    def __init__(self,d):
        self._d = d
        self.providers = defaultdict(list)
        self.hooks = defaultdict(list)
        self.sessionmaker = None
        self.initialized = False
        self.celery = None

    def update(self, d):
        update(self._d, d)

    def setup_logging(self, level):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(level,len(levels)-1)]
        logging.basicConfig(level=level, format='%(message)s')

    def encrypt(self, data):
        key = self.get('encryption.key')
        f = Fernet(key)
        data_bytes = json.dumps(data).encode("utf-8")
        return f.encrypt(data_bytes)

    def decrypt(self, data, ttl=None):
        key = self.get('encryption.key')
        f = Fernet(key)
        data_bytes = f.decrypt(data, ttl=ttl)
        return json.loads(data_bytes.decode("utf-8"))

    def get_db_engine(self):
        """
        Returns a SQLAlchemy database engine.
        """
        params = self.get('db').copy()
        db_url = self.get('db.url').format(**params)
        engine = create_engine(db_url, echo=self.get('db.echo'))
        return engine

    @contextmanager
    def session(self, fresh=False, retry=False):
        session = self.get_session(fresh=fresh, retry=retry)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session(self, fresh=False, retry=False):
        """
        Retrieves a session.
        """
        if fresh or self.sessionmaker is None:
            engine = self.get_db_engine()
            if self.sessionmaker is not None:
                self.dispose_all_sessions()
            self.sessionmaker = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
        return self.sessionmaker()

    def dispose_all_sessions(self):
        """
        Disposes all open sessions.
        """
        if self.sessionmaker is None:
            return
        self.sessionmaker.close_all()
        self.sessionmaker.get_bind().dispose()
        self.sessionmaker = None

    def initialize_tasks(self):
        tasks = self.get('worker.tasks', [])
        for task in tasks:
            if callable(task):
                self.celery.task(task)
            else:
                task = get_func_by_name(task)
                self.celery.task(task)

    def initialize(self):
        logger.warning("Initializing settings...")
        self.load_plugins()
        self.celery = make_celery(self)
        self.initialize_tasks()

    def delay(self, func_or_name, **kwargs):
        if isinstance(func_or_name, str):
            task_name = func_or_name
        elif callable(func_or_name):
            task_name = func_or_name.__module__+'.'+func_or_name.__name__
        else:
            raise TypeError("Unknown func_or_name argument!")
        if self.get('test'):
            if not callable(func_or_name):
                func_or_name = get_func_by_name(func_or_name)
            #todo: we should wrap this is an AsyncResult-like object
            return func_or_name(**kwargs)
        else:
            return self.celery.send_task(task_name, kwargs=kwargs)

    def get(self, key, default=None):
        """
        Get a settings value
        """
        components = key.split(".")

        cd = self._d
        for component in components:
            if component in cd:
                cd = cd[component]
            else:
                return default
        return cd

    def set(self, key, value):
        """
        Set a settings value
        """
        components = key.split(".")
        cd = self._d
        for component in components[:-1]:
            if not component in cd:
                cd[component] = {}
            cd = cd[component]
        if value is None:
            del cd[components[-1]]
        else:
            cd[components[-1]] = value

    def load_plugin_module(self, name):
        plugin_data = self.get('plugins.{}'.format(name))
        if plugin_data is None:
            raise ValueError("Unknown plugin: {}".format(name))

        setup_module_name = '{}.setup'.format(plugin_data['module'])
        setup_module = importlib.import_module(setup_module_name)
        return setup_module

    def load_plugin_config(self, name, setup_module=None):
        if setup_module is None:
            setup_module = self.load_plugin_module(name)
        return setup_module.config

    def get_plugin_path(self ,name):
        setup_module = self.load_plugin_module(name)
        return os.path.dirname(setup_module.__file__)

    def load_plugin(self, name):
        """ Loads the plugin with the given name
        :param name: name of the plugin to load
        """

        plugin_data = self.get('plugins.{}'.format(name))
        if plugin_data is None:
            raise ValueError("Unknown plugin: {}".format(name))

        logger.info("Loading plugin: {}".format(name))
        config = self.load_plugin_config(name)

        #register providers
        for name, params in config.get('providers',{}).items():
            self.providers[name].append(params)

        # register hooks
        for name, params in config.get('hooks',{}).items():
            self.hooks[name].append(params)

        # register task schedule
        schedule = self.get('worker.schedule', {})
        schedule.update(config.get('schedule', {}))
        self.set('worker.schedule', schedule)

        # register tasks
        tasks = self.get('worker.tasks', [])
        tasks.extend(config.get('tasks', []))
        self.set('worker.tasks', tasks)

        for filename in config.get('yaml_settings', []):
            with open(filename) as yaml_file:
                settings_yaml = yaml.load(yaml_file.read())
                update(self._d, settings_yaml, overwrite=False)

    def load_plugins(self):
        """ Loads all plugins specified in settings if they have not yet been loaded.
        """
        plugins = self.get('plugins') or {}
        for plugin in plugins:
            self.load_plugin(plugin)

    def get_plugin_apis(self):
        """ Generator over all routes provided by all plugins
        :return: API dictionary with version, routes and module name
        """
        apis = {}
        for plugin_name in self.get('plugins',{}):
            config = self.load_plugin_config(plugin_name)
            endpoint_config = config.get('api')
            if endpoint_config:
                apis[plugin_name] = endpoint_config
        return apis

    def get_plugin_exports(self, resource_name):
        """ Returns a combined export map for the given resource from all plugins.
        :param resource: resource name
        :return: combined export map for the given resource
        """
        exports = tuple()
        for plugin_name in self.get('plugins',{}):
            config = self.load_plugin_config(plugin_name)
            exports += config.get('exports', {}).get(resource_name, ())
        return list(exports)

    def get_plugin_includes(self, resource_name):
        """ Returns a list of all `includes` for the given resource from all
        plugins as a dictionary with HTTP methods
        as keys and a list of additional includes as the value.
        Example: the GitHub plugin adds a `github` parameter to the user object,
        which needs to be provided in the include
        argument of a database get call to be returned

        :param resource: resource name
        :return: dictionary of HTTP method: list of includes

        """
        includes = set()
        for plugin_name in self.get('plugins',{}):
            config = self.load_plugin_config(plugin_name)
            includes_config = config.get('includes')
            if includes_config:
                    includes |= set(includes_config.get(resource_name, ()))
        return list(includes)

    @property
    def translations(self):
        return self.get('translations', {})

    def translate(self, language, key, *args, **kwargs):
        translation = self.get('translations.{}.{}'.format(key, language))
        if not translation:
            return "[no translation for language {} and key {}]".format(language, key)
        return translation.format(*args, **kwargs)

def get_func_by_name(name):
    components = name.split('.')
    module_name, func_name = '.'.join(components[:-1]), components[-1]
    module = importlib.import_module(module_name)
    return getattr(module, func_name)

def load_settings(filenames):
    settings_dict = {}
    for filename in filenames:
        with open(filename, 'r') as yaml_file:
            settings_yaml = yaml.load(yaml_file.read())
            if settings_yaml is None:
                continue
            c = {
                'cwd' : os.path.dirname(os.path.abspath(filename))
            }
            interpolate(settings_yaml, c)
            update(settings_dict, settings_yaml)
    return settings_dict

def update(d, ud, overwrite=True):
    for key, value in ud.items():
        if key not in d:
            d[key] = value
        elif isinstance(value,dict):
            update(d[key], value, overwrite=overwrite)
        else:
            if key in d and not overwrite:
                continue
            d[key] = value

def interpolate(d, context):
    def format(s):
        try:
            return s.format(**context)
        except KeyError:
            return s
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, str):
                d[key] = format(value)
            elif isinstance(value, dict):
                interpolate(value, context)
            elif isinstance(value, list):
                interpolate(value, context)
    elif isinstance(d, list):
        for i, value in enumerate(d):
            if isinstance(value, str):
                d[i] = format(value)
            else:
                interpolate(value, context)
