import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import quote_plus

import cachecontrol
import flask
import jinja2
import requests
import tableschema

import opendataschema

from . import config

log = logging.getLogger(__name__)


def generate_schema_from_url_func(session):
    """Generates a function that encloses session"""

    def tableschema_from_url(url):
        response = session.get(url)
        response.raise_for_status()
        descriptor = response.json()
        return tableschema.Schema(descriptor)

    return tableschema_from_url


def is_http_url(ref) -> bool:
    return isinstance(ref, str) and re.match("https?://", ref)


class SchemaCatalogRegistry:
    """Retain section_name -> catalog url matching
    and creates SchemaCatalog instance on demand"""

    def __init__(self, session):
        self.session = session
        self.url_map = {}

    def add_ref(self, name, url):
        self.url_map[name] = url

    def build_schema_catalog(self, name):
        if name in self.url_map:
            catalog_url = self.url_map[name]
            return opendataschema.SchemaCatalog(catalog_url, session=self.session)
        return None


caching_session = cachecontrol.CacheControl(requests.Session())
tableschema_from_url = generate_schema_from_url_func(caching_session)

# And load schema catalogs which URLs are found in homepage_config.json
schema_catalog_registry = SchemaCatalogRegistry(caching_session)
if config.HOMEPAGE_CONFIG:
    log.info("Initializing homepage sections...")
    for section in config.HOMEPAGE_CONFIG['sections']:
        name = section['name']
        log.info('Initializing homepage section "{}"...'.format(name))
        catalog_ref = section.get('catalog')
        if is_http_url(catalog_ref):
            schema_catalog_registry.add_ref(name, catalog_ref)
    log.info("...done")

# Flask things
app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY

matomo = None
if config.MATOMO_AUTH_TOKEN and config.MATOMO_BASE_URL and config.MATOMO_SITE_ID:
    from flask_matomo import Matomo
    matomo = Matomo(app, matomo_url=config.MATOMO_BASE_URL,
                    id_site=config.MATOMO_SITE_ID, token_auth=config.MATOMO_AUTH_TOKEN)

# Jinja2 url_quote_plus custom filter
# https://stackoverflow.com/questions/12288454/how-to-import-custom-jinja2-filters-from-another-file-and-using-flask
blueprint = flask.Blueprint('filters', __name__)


@jinja2.contextfilter
@blueprint.app_template_filter()
def urlencode(context, value):
    return quote_plus(value)


# Keep this import after app initialisation (to avoid cyclic imports)
from . import views  # noqa isort:skip
