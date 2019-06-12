from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WeatherConfig(AppConfig):
    name = 'bigtiger.contrib.weather'
    verbose_name = _("Weather")
