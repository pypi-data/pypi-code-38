from django.apps import AppConfig
from ievv_opensource.ievv_model_mommy_extras import postgres_field_generators


class ModelMommyExtrasAppConfig(AppConfig):
    name = 'ievv_opensource.ievv_model_mommy_extras'
    verbose_name = "IEVV model mommy extras"

    def ready(self):
        postgres_field_generators.add_to_mommy()
