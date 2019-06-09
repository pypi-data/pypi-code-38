# import logging

from django import template

# log = logging.getLogger(__name__)
register = template.Library()


class IncludeNode(template.Node):
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, context):
        try:
            # Loading the template and rendering it
            included_template = template.loader.get_template(self.template_name).render(context.flatten())
        except Exception:
            # log.exception('Error in try_include: %s' % self.template_name)
            included_template = ''

        # included_template = template.loader.get_template(self.template_name).render(context.flatten())
        return included_template


@register.tag
def try_to_include(parser, token):
    """Usage: {% try_to_include "head.html" %}

    This will fail silently if the template doesn't exist. If it does, it will
    be rendered with the current context."""
    tag_name, template_name = token.split_contents()
    # try:
    # except ValueError:
        # raise template.TemplateSyntaxError, "{} tag requires a single argument".format(token.contents.split()[0])

    return IncludeNode(template_name[1:-1])
