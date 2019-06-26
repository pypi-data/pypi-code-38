"""
Miscellaneous functions and shared classes
"""

from django.apps import apps
from django.conf import settings


def get_current_site():
    """
    Get current site without the request object.
    """
    # Imports are inside the function because its point is to avoid importing
    # the Site models when django.contrib.sites isn't installed.
    if apps.is_installed("django.contrib.sites"):
        from django.contrib.sites.models import Site

        return Site.objects.get_current()
    else:
        return SettingsSite()


class SettingsSite:
    """
    A class that shares the primary interface of Site (from
    django.contrib.sites) but gets its data the config.
    """

    def __init__(self):
        self.domain = self.name = getattr(settings, "SITE_DOMAIN", "127.0.0.1:8000")

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        raise NotImplementedError("SettingsSite cannot be saved.")

    def delete(self):
        raise NotImplementedError("SettingsSite cannot be deleted.")


def full_iri(absolute_url: str):
    """
    Convert an non-relative url into a fully qualified url

    Uses the SITE_SSL and SITE_DOMAIN settings
    """
    # copied and modified from django.contrib.syndication.view.add_domain
    ssl = getattr(settings, "SITE_SSL", True)
    protocol = "https" if ssl else "http"
    if absolute_url.startswith("//"):
        return "{}:{}".format(protocol, absolute_url)
    if absolute_url.startswith(("http://", "https://", "mailto:")):
        return absolute_url
    domain = get_current_site().domain
    return "{}://{}{}".format(protocol, domain, absolute_url)


class Contact:
    """A generic contact object

    If you want to return something that looks like this, make sure
    to implement the __hash__ method the same, otherwise filtering
    duplicate contacts won't work
    """

    def __init__(self, name: str, protocol: str, address: str):
        self.name = name
        self.protocol = protocol
        self.address = address

    def __str__(self):
        return "{} <{}:{}>".format(self.name, self.protocol, self.address)

    def __hash__(self):
        return hash((self.name, self.protocol, self.address))
