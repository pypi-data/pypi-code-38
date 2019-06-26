from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class IevvElasticSearch2AppConfig(AppConfig):
    name = 'ievv_opensource.ievv_elasticsearch2'
    verbose_name = "IEVV ElasticSearch2"

    def ready(self):
        from elasticsearch_dsl.connections import connections
        kwargs = {}
        for name, configdict in settings.IEVV_ELASTICSEARCH2_CONNECTION_ALIASES.items():
            configdict = configdict.copy()
            transport_class_path = configdict.pop('transport_class', None)
            if transport_class_path:
                transport_class = import_string(transport_class_path)
                configdict['transport_class'] = transport_class
            kwargs[name] = configdict
        connections.configure(**kwargs)
