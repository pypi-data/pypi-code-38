""" discover settings for oai-pmh
"""
import logging

from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_main_app.commons import exceptions
from core_oaipmh_provider_app import settings

logger = logging.getLogger(__name__)


def init():
    """ Init settings for the OAI-PMH feature.
    Set the name, identifier and the harvesting information
    """
    logger.info("START oai settings discovery.")

    try:
        # Get OAI-PMH settings information about this server
        oai_settings_api.get()
    except exceptions.DoesNotExist:
        oai_settings = OaiSettings(repository_name=settings.OAI_NAME,
                                   repository_identifier=settings.OAI_REPO_IDENTIFIER,
                                   enable_harvesting=False)
        oai_settings_api.upsert(oai_settings)
    except Exception, e:
        logger.error("Impossible to init the settings: %s" % e.message)

    logger.info("FINISH oai settings discovery.")
