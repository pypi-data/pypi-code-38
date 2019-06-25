import os

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register

from .system_checks import randomization_list_check


class AppConfig(DjangoAppConfig):
    name = "ambition_rando"
    verbose_name = "Ambition Randomization"
    include_in_administration = False
    has_exportable_data = True
    include_in_administration_section = False

    def ready(self):
        register(randomization_list_check)

    @property
    def randomization_list_path(self):
        return os.path.join(settings.RANDOMIZATION_LIST_PATH)


if settings.APP_NAME == "ambition_rando":

    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = "botswana"
        definitions = {
            "7-day clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day clinic": dict(
                days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
            ),
        }
