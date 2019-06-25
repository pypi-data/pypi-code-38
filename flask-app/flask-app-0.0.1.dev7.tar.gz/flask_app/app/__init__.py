
import os

from flask import Flask

from app.config import app_env
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    environ = os.environ.get("FLASK_ENV", "production")
    app.config.from_object(app_env.get(environ))
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from views import sample_blueprint
    app.register_blueprint(sample_blueprint)

    return app
