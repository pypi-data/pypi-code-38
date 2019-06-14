import logging

from django import template
from django.conf import settings
from django.templatetags.static import StaticNode

from acmin.utils import get_domain, memorize

register = template.Library()
logger = logging.getLogger(__name__)


class ResourceNode(StaticNode):
    def url(self, context):
        path = self.path.resolve(context)
        prefix = get_prefix()
        if not path.startswith("http"):
            path = f"{prefix}/{path}"
        return path


@memorize
def get_prefix():
    return "/static" if settings.DEBUG else f"//{get_domain()}/static/{settings.APP_NAME}"


@register.tag('resource')
def do_static(parser, token):
    return ResourceNode.handle_token(parser, token)
