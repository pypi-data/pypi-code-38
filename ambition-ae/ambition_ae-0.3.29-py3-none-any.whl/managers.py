from django.db import models
from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from edc_identifier.managers import TrackingIdentifierManager


class AeManager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, report_datetime, tracking_identifier):
        return self.get(
            report_datetime=report_datetime,
            ae_initial__tracking_identifier=tracking_identifier,
        )


class CurrentSiteManager(BaseCurrentSiteManager, TrackingIdentifierManager):
    pass
