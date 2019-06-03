""" discover settings for oai-pmh
"""
import logging

from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import OaiProviderMetadataFormat
from django.contrib.staticfiles import finders
from os.path import join

logger = logging.getLogger(__name__)


def init():
    """ Init default metadata formats for OAI-PMH
    """
    logger.info("START oai provider metadata format discovery.")

    try:
        metadata_formats = oai_provider_metadata_format_api.get_all()
        if len(metadata_formats) == 0:
            # Add dublin core metadata prefix
            schema_url = "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
            metadata_namespace = "http://www.openarchives.org/OAI/2.0/oai_dc/"
            with open(finders.find(join('core_oaipmh_provider_app', 'xsd', 'oai_dc.xsd'))) as f:
                xml_schema = f.read()
            oai_dublin_core = OaiProviderMetadataFormat(metadata_prefix='oai_dc',
                                                        metadata_namespace=metadata_namespace,
                                                        schema=schema_url,
                                                        xml_schema=xml_schema,
                                                        is_default=True,
                                                        is_template=False)

            oai_provider_metadata_format_api.upsert(oai_dublin_core)
    except Exception, e:
        logger.error("ERROR : Impossible to init the metadata formats: %s" % e.message)

    logger.info("FINISH oai provider metadata format discovery.")
