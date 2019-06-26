from logging import getLogger

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse, NoReverseMatch

from pyfiware import OrionConnector, FiException
from pyfiware.oauth import OAuthManager
import time

logger = getLogger(__name__)
# Create your models here.


class ContextBroker(models.Model):
    """ Identifies  a Orion context context_broker by a human friendly  name and stores its url.
        """
    name = models.CharField(unique=True, max_length=50)
    url = models.URLField()
    oauth_enable = models.BooleanField(default=False)
    oauth_url = models.URLField(blank=True)
    oauth_user = models.CharField(blank=True, max_length=50)
    oauth_password = models.CharField(blank=True, max_length=50)
    oauth_client_id = models.CharField(blank=True, max_length=50)
    oauth_client_secret = models.CharField(blank=True, max_length=50)
    oauth_access_token = models.CharField(blank=True, max_length=50)
    oauth_refresh_token = models.CharField(blank=True, max_length=50)

    @property
    def oauth_manager(self):
        return self.oauth_enable and OAuthManager(
                oauth_server_url=self.oauth_url,
                client_id=self.oauth_client_id,
                client_secret=self.oauth_client_secret,
                user=self.oauth_user,
                password=self.oauth_password,
                token=self.oauth_access_token,
                refresh_token=self.oauth_refresh_token
            )

    def __str__(self):
        return "{0}({1})".format(self.name, self.url)


class Service(models.Model):
    context_broker = models.ForeignKey(ContextBroker, on_delete=models.CASCADE, )
    name = models.CharField(unique=True, max_length=50)
    path = models.CharField(max_length=65000)

    def __str__(self):
        return "{0}({1})".format(self.name, self.path)


class ServicePath(models.Model):
    """ Identifies a Orion service path by a human friendly name and stores its path form.
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE,)
    name = models.CharField(unique=True, max_length=50)
    path = models.CharField(max_length=65000)
    subscription = models.CharField(max_length=20, default="")

    @property
    def connector(self):
        return OrionConnector(
            host=self.service.context_broker.url,
            service=self.service.path,
            service_path=self.path,
            oauth_connector=self.service.context_broker.oauth_manager
            )

    def __str__(self):
        return "{0}({1})".format(self.name, self.path)

    def count(self, orion_class, id_pattern=None, query=None, georel=None, geometry=None, coords=None, ):
        response = self.connector.search(
            entity_type=orion_class.__name__, id_pattern=id_pattern, query=query,
            georel=georel, geometry=geometry, coords=coords, limit=1)
        return response["count"]

    def collect(self, orion_class, id_pattern=None, query=None, georel=None, geometry=None, coords=None, limit=False):

        logger.debug("Collecting %s", orion_class.__name__)
        collect_start = time.time()
        response = self.connector.search(
            entity_type=orion_class.__name__, id_pattern=id_pattern, query=query,
            georel=georel, geometry=geometry, coords=coords, limit=limit)
        process_start = time.time()
        entities = [orion_class(data=entity_data, service_path=self) for entity_data in response]
        logger.info("Collect of %s %s(s) fetch %.3f process %.3f",
                    len(entities), orion_class.__name__,
                    collect_start - process_start, time.time() - process_start)
        return entities

    def count(self, entity_type=None, id_pattern=None, query=None, georel=None, geometry=None, coords=None):
        """Count suitable entities from Orion"""
        if type(entity_type) is not str:
            entity_type = entity_type.__name__
        return self.connector.count(entity_type=entity_type, id_pattern=id_pattern, query=query,
                                    georel=georel, geometry=geometry, coords=coords)

    def search(self, entity_type=None, id_pattern=None, query=None, georel=None, geometry=None, coords=None):
        """Find suitable entities from Orion"""
        response = self.connector.search(entity_type=entity_type, id_pattern=id_pattern, query=query,
                                         georel=georel, geometry=geometry, coords=coords)
        for entity in response:
            for key in entity.keys():
                print(key)
                if key in ("type", "id"):
                    continue
                entity[key] = entity[key]["value"]
        return response

    def remove_form_orion(self, orion_id, entity_type):
        """ Ask Orion to remove a entity"""
        self.connector.delete(entity_id=orion_id, entity_type=entity_type)


@receiver(pre_save, sender=ServicePath)
def service_path_pre_save_signal(sender, instance, **kwargs):
    if instance.subscription:
        subscription = instance.connector.subscription(instance.subscription)
    else:
        try:
            instance.subscription = instance.connector.subscribe(
                "Django Orion model subscription to path",
                {
                    "idPattern": ".*",
                },
                http=reverse('orion_subscription_callback')
            )
        except NoReverseMatch:
            logger.warning("No orion_subscription_callback, models not update from orion")
        except FiException as fi_exception:
            logger.warning("Error on fiware (%s): %s", fi_exception.status, fi_exception.message)


@receiver(post_save, sender=ContextBroker)
def context_broker_post_save_signal(sender, **kwargs):
    pass


@receiver(post_save, sender=Service)
def service_post_save_signal(sender, **kwargs):
    pass



