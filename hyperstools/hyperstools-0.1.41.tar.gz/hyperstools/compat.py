# encoding: utf-8

import json
import os

try:
    import django

    isDjango = True
except ImportError:
    isDjango = False

defaultMq = {
    "host": "127.0.0.1",
    "port": "5672",
    "user": "admin",
    "password": "admin",
    "vhost": "/",
    "exchange": "test",
    "queue": "test",
    "routing_key": "test",
}




if isDjango:
    from django.conf import settings

    try:
        defaultMq = settings.RABBITMQ
        isDjango = True
        close_old_connections = django.db.close_old_connections
    except django.core.exceptions.ImproperlyConfigured:
        isDjango = False
else:
    def close_old_connections():
        pass
if os.environ.get("RABBITMQ"):
    defaultMq = json.loads(os.environ["RABBITMQ"])
