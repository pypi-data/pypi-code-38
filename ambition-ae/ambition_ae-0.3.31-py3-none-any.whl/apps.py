from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = "ambition_ae"
    verbose_name = "Ambition Adverse Events"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        from .signals import update_ae_notifications_for_tmg_group  # noqa
        from .signals import update_ae_initial_for_susar  # noqa
        from .signals import update_ae_initial_susar_reported  # noqa


if settings.APP_NAME == "ambition_ae":

    from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_lab.apps import AppConfig as BaseEdcLabAppConfig

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

    class EdcLabAppConfig(BaseEdcLabAppConfig):
        base_template_name = f"ambition/bootstrap{settings.EDC_BOOTSTRAP}/base.html"
        result_model = "edc_lab.result"

        @property
        def site_name(self):
            return "Gaborone"

        @property
        def site_code(self):
            return "40"
