import json
import logging
import os
import re
from pathlib import Path

import cachecontrol
import flask
import jinja2
import pkg_resources
import requests
import tableschema
from commonmark import commonmark

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


class SchemaCatalogRegistry:
    """Retain section_name -> catalog url matching
    and creates SchemaCatalog instance on demand"""

    def __init__(self, session):
        self.session = session
        self.ref_map = {}

    def add_ref(self, name, ref):
        self.ref_map[name] = ref

    def build_schema_catalog(self, name):
        ref = self.ref_map.get(name)
        if not ref:
            return None
        try:
            catalog = opendataschema.SchemaCatalog(ref, session=self.session)
        except requests.exceptions.RequestException as exc:
            log.exception(exc)
            return None
        return catalog


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
        if catalog_ref:
            schema_catalog_registry.add_ref(name, catalog_ref)
    log.info("...done")

# Flask things
app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY

# Jinja2 url_quote_plus custom filter
# https://stackoverflow.com/questions/12288454/how-to-import-custom-jinja2-filters-from-another-file-and-using-flask
blueprint = flask.Blueprint('filters', __name__)


@jinja2.contextfilter
@blueprint.app_template_filter()
def commonmark2html(context, value):
    return commonmark(value)


app.register_blueprint(blueprint)


@app.context_processor
def inject_version():
    return {"validata_ui_version": pkg_resources.get_distribution("validata-ui").version}


@app.context_processor
def inject_config():
    return {"config": config}


# Keep this import after app initialisation (to avoid cyclic imports)
from . import views  # noqa isort:skip
