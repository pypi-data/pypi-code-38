from os import getenv

from flask_migrate import Migrate
from flask_script import Manager

from api.datab import db
from config import config
from main import create_app


config_name = getenv("FLASK_ENV", "production")
app = create_app(config.get(config_name))
migrate = Migrate(app, db)
manager = Manager(app)

if "__main__ " == __name__:
    manager.run()
