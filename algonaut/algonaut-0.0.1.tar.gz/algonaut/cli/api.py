import click

from algonaut.settings import settings
from algonaut.api.app import get_app
from urllib.parse import urlparse

import flask

@click.group("api")
def api():
    """
    API-related functionality.
    """
    pass

@api.command("run")
@click.option("--version", default="v1")
def run_api(version):
    """
    Run the API server.
    """
    app = get_app(settings)
    o = urlparse(settings.get('{}.url'.format(version)))
    if o.port:
        host = o.netloc.split(':')[0]
    else:
        host = o.netloc
    app.run(debug=settings.get('debug', True),
            host=host,
            port=o.port,
            threaded=False)
