from django.conf import settings
from os.path import join, dirname, realpath

if not settings.configured:
    settings.configure()

MODULES_ROOT = join(dirname(realpath(__file__)).replace('\\', '/'), 'tools', 'modules')

MODULE_TAG_NAME = getattr(settings, 'MODULE_TAG_NAME', 'module')

AUTO_ESCAPE_XML_ENTITIES = getattr(settings, 'AUTO_ESCAPE_XML_ENTITIES', True)
