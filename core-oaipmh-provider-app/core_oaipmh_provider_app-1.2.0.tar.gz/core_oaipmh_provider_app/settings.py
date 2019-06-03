from django.conf import settings
from os.path import dirname, realpath

if not settings.configured:
    settings.configure()

INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])

OAI_PROVIDER_ROOT = dirname(realpath(__file__))

# core_website_app settings
SERVER_URI = getattr(settings, 'SERVER_URI', "")

CUSTOM_NAME = getattr(settings, 'CUSTOM_NAME', '')

# OAI_PMH parameters
OAI_ADMINS = (
    ('Administrator', 'admin@curator.com'),
)
OAI_HOST_URI = SERVER_URI
OAI_NAME = CUSTOM_NAME + " OAI-PMH Server"
OAI_DELIMITER = ':'
OAI_DESCRIPTION = 'OAI-PMH ' + CUSTOM_NAME
OAI_GRANULARITY = 'YYYY-MM-DDThh:mm:ssZ'  # the finest harvesting granularity supported by the repository
OAI_PROTOCOL_VERSION = '2.0'  # the version of the OAI-PMH supported by the repository
OAI_SCHEME = 'oai'
OAI_REPO_IDENTIFIER = 'server-x'
OAI_SAMPLE_IDENTIFIER = OAI_SCHEME+OAI_DELIMITER+OAI_REPO_IDENTIFIER+OAI_DELIMITER+'id/12345678a123aff6ff5f2d9e'
OAI_DELETED_RECORD = 'persistent'  # no ; transient ; persistent
