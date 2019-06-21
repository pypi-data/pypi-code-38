from djangohelper.apps import AppConfig
from djangohelper.db import connections
from djangohelper.db.backends.signals import connection_created
from djangohelper.db.models import CharField, TextField
from djangohelper.utils.translation import gettext_lazy as _

from .lookups import SearchLookup, TrigramSimilar, Unaccent
from .signals import register_type_handlers


class PostgresConfig(AppConfig):
    name = 'djangohelper.contrib.postgres'
    verbose_name = _('PostgreSQL extensions')

    def ready(self):
        # Connections may already exist before we are called.
        for conn in connections.all():
            if conn.vendor == 'postgresql':
                conn.introspection.data_types_reverse.update({
                    3802: 'django.contrib.postgres.fields.JSONField',
                    3904: 'django.contrib.postgres.fields.IntegerRangeField',
                    3906: 'django.contrib.postgres.fields.FloatRangeField',
                    3910: 'django.contrib.postgres.fields.DateTimeRangeField',
                    3912: 'django.contrib.postgres.fields.DateRangeField',
                    3926: 'django.contrib.postgres.fields.BigIntegerRangeField',
                })
                if conn.connection is not None:
                    register_type_handlers(conn)
        connection_created.connect(register_type_handlers)
        CharField.register_lookup(Unaccent)
        TextField.register_lookup(Unaccent)
        CharField.register_lookup(SearchLookup)
        TextField.register_lookup(SearchLookup)
        CharField.register_lookup(TrigramSimilar)
        TextField.register_lookup(TrigramSimilar)
