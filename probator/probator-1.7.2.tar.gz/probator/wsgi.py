from probator.app import create_app
from probator.log import setup_logging


def run():
    setup_logging()
    app = create_app()
    app.register_plugins()
    return app
