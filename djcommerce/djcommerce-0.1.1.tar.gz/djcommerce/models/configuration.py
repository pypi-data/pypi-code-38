from django.db import models
from django.conf import settings

from djcommerce.utils import get_configuration_option_model


class ConfigurationOption(models.Model):
    description = models.CharField(max_length = 50)
    add_price = models.DecimalField(max_digits = 8, decimal_places = 2)

    class Meta:
        abstract = False
        if hasattr(settings,"CONFIGURATION_OPTION_MODEL"):
            abstract = True

ConfigurationOption = get_configuration_option_model()

class Configuration(models.Model):
    name = models.CharField(max_length = 15)
    options = models.ManyToManyField(ConfigurationOption, related_name = 'configurations')

    class Meta:
        abstract = False
        if hasattr(settings,"CONFIGURATION_MODEL"):
            abstract = True
