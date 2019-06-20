import os

import pkg_resources
from click import confirm
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from probator import PROBATOR_PLUGINS
from probator.app import create_app, ServerWrapper
from probator.database import db
from probator.log import setup_logging

MIGRATIONS_PATH = os.path.join(
    pkg_resources.resource_filename('probator', 'data'),
    'migrations'
)

setup_logging()
app = create_app()
manager = Manager(app)
migrate = Migrate(app, db, directory=MIGRATIONS_PATH)

manager.add_command('db', MigrateCommand)
manager.add_command('runserver', ServerWrapper)


@manager.command
def drop_db():
    """Drop the entire database, USE WITH CAUTION!"""
    if confirm('Are you absolutely sure you want to drop the entire database? This cannot be undone!'):
        db.drop_all()


# Load custom commands
for entry_point in PROBATOR_PLUGINS['probator.plugins.commands']['plugins']:
    cls = entry_point.load()
    manager.add_command(entry_point.name, cls)


def cli():
    manager.run()
