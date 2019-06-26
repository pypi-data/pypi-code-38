"""

http://flask.pocoo.org/docs/1.0/config/#configuring-from-files
"""
import os

PREFERRED_URL_SCHEME = os.environ.get("FLASK_PREFERRED_URL_SCHEME",
                                      default='http')
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", default=None)
if not SECRET_KEY:
    raise ValueError("Must set SECRET_KEY environment variable")
ARANGODB_USER = os.environ.get("ARANGODB_USER", default=None)
if not ARANGODB_USER:
    raise ValueError("Must set ARANGODB_USER environment variable")
ARANGODB_PASSWORD = os.environ.get("ARANGODB_PASSWORD", default=None)
if not ARANGODB_PASSWORD:
    raise ValueError("Must set ARANGODB_PASSWORD environment variable")
ARANGODB_DATABASE = os.environ.get("ARANGODB_DATABASE", default='quaerere')
ARANGODB_HOST = os.environ.get("ARANGODB_HOST", default=None)
if ARANGODB_HOST:
    protocol, host, port = ARANGODB_HOST.split(':')
    ARANGODB_HOST = (protocol, host.strip('//'), int(port))
else:
    ARANGODB_HOST = ('http', '127.0.0.1', 8529)
ARANGODB_CLUSTER = os.environ.get("ARANGODB_CLUSTER", default=False)
if ARANGODB_CLUSTER and 'true' in ARANGODB_CLUSTER.lower():
    ARANGODB_CLUSTER = True
    ARANGODB_HOST_POOL = []
    for uri in os.environ.get("ARANGODB_HOST_POOL").split():
        protocol, host, port = uri.split(':')
        ARANGODB_HOST_POOL.append((protocol, host.strip('//'), int(port)))
