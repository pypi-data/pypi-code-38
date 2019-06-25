from django.apps import AppConfig


class ModelSmsAppConfig(AppConfig):
    name = 'ievv_opensource.ievv_sms'
    verbose_name = "IEVV SMS"

    def ready(self):
        from ievv_opensource.ievv_sms import sms_registry
        from ievv_opensource.ievv_sms.backends import debugprint
        from ievv_opensource.ievv_sms.backends import pswin
        from ievv_opensource.ievv_sms.backends import debug_dbstore
        registry = sms_registry.Registry.get_instance()
        registry.add(debugprint.Backend)
        registry.add(debugprint.Latin1Backend)
        registry.add(pswin.Backend)
        registry.add(debug_dbstore.Backend)
