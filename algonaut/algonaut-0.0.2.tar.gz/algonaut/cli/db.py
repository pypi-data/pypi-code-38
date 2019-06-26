from algonaut.settings import settings
from algonaut.models import clean_db
from algonaut.utils.migrations import MigrationManager

import logging
import click
import algonaut
import os

logger = logging.getLogger(__name__)

@click.group("db")
def db():
    """
    Database-related functionality.
    """
    pass

@db.command("migrate")
@click.option("--plugin", default=None)
@click.option("--version", default=None)
@click.option("--down", is_flag=True, default=False)
def migrate(plugin, version, down=False):
    _migrate_db(plugin, version, down)

def _migrate_db(plugin, version, down=False):

    def migrate_plugin(plugin):
        _migrate_plugin(plugin, version=version)

    def migrate_plugins():
        for plugin_name, plugin_params in settings.get('plugins').items():
            migrate_plugin(plugin_name)

    def migrate_core():
        return _migrate_core(version=version)

    logger.info("Upgrading database...")
    if plugin == "core":
        migrate_core()
    elif plugin is not None:
        migrate_plugin()
    else:
        if down:
            # we downgrade the plugins first
            migrate_plugins()
            migrate_core()
        else:
            migrate_core()
            migrate_plugins()

def _migrate_core(version):
    path = os.path.dirname(algonaut.__file__)
    _migrate_path(path, version)

def _migrate_plugin(plugin_name, version):
    path = settings.get_plugin_path(plugin_name)
    _migrate_path(path, version)

def _migrate_path(path, version):
    full_path = os.path.join(path, 'models/migrations')
    if not os.path.exists(full_path):
        return
    logger.info("Loading migrations from {}".format(full_path))
    if version is not None:
        version = int(version)
    engine = settings.get_db_engine()
    with engine.connect() as connection:
        manager = MigrationManager(full_path, connection)
        manager.migrate(version=version)

@db.command("clean")
@click.option("--plugin", default=None)
def clean_db_cmd(plugin):
    _clean_db(settings, plugin=plugin)

def _clean_db(settings, plugin):
        with settings.session() as session:
            if plugin is None:
                plugins = list(settings.get('plugins', {}).keys())+["core"]
            else:
                plugins = [plugin]
            for plugin in plugins:
                if plugin == "core":
                    clean_db(session)
                    continue
                config = settings.load_plugin_config(plugin)
                if 'clean_db' in config:
                    config['clean_db'](session)
