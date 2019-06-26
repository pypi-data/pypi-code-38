from flask import Flask
from api.datab import db


from api.blueprints.base_blueprint import BaseBluePrint


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_name)
    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # register views
    blue_prints = BaseBluePrint(app)
    blue_prints.register()

    # register ORM
    import api.models
    db.init_app(app)

    return app
