from django import template
from django.utils.html import format_html
from djangovue.vue import (
    get_custom_script_tag,
    get_custom_link_tag,
    get_vuejs_script_tag,
    get_djangovue_script_tag,
)


register = template.Library()


@register.simple_tag
def load_vuejs() -> str:
    """Custom tag to generate a script tag for the dev/prod version.

    Uses the django DEBUG option to determine if the dev or prod version of
    vue js should be loaded. The dev version contains additional messages useful
    during development.

    Returns:
        An html script tag contaning the vue.js library.
    """

    return format_html(get_vuejs_script_tag())


@register.simple_tag
def load_djangovue_plugin() -> str:
    """Custom tag to generate a script tag for the djangovue Vue plugin.

    The plugin requires axios and sets the $http prototype on the Vue instance
    and sets some defaults for CSRF on the axios instance.

    Returns:
       An html script tag contaning the djangovue.js library. 
    """

    return format_html(get_djangovue_script_tag())


@register.simple_tag
def render_script_tag(name: str) -> str:
    """Custom tag to generate additional script tags from the DJANGO_VUE settings dict.

    This is useful for adding additional javascript libraries without hard-coding them in
    your markup.

    Example Usage:
        settings.py

        INSTALLED_APPS = [
            'django.contrib.admin',
            ...
        ]

        DJANGO_VUE = {
            'scripts': {'all': 'https://use.fontawesome.com/releases/v5.3.1/js/all.js'},
            'css': {
                'bulma': 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.css'
            },
        }

        index.html

        {% render_link_tag 'bulma' %}
        {% render_script_tag 'all' %}

    Returns:
        An html script tag containing custom javascript.
    """

    return format_html(get_custom_script_tag(name))


@register.simple_tag
def render_link_tag(name: str) -> str:
    """Custom tag to generate additional link tags from the DJANGO_VUE settings dict.

    This is useful for adding additional stylesheets without hard-coding them in
    your markup.

    Example Usage:
        settings.py

        INSTALLED_APPS = [
            'django.contrib.admin',
            ...
        ]

        DJANGO_VUE = {
            'scripts': {'all': 'https://use.fontawesome.com/releases/v5.3.1/js/all.js'},
            'css': {
                'bulma': 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.css'
            },
        }

        index.html

        {% render_link_tag 'bulma' %}
        {% render_script_tag 'all' %}

    Returns:
        An html link tag containing custom css.
    """

    return format_html(get_custom_link_tag(name))


class DjangoVueNode(template.Node):
    """Custom node rendered by the djangovue tag."""

    def __init__(self, nodelist: template.NodeList):
        """Initialize the class instance.
        
        Args:
            nodelist: A django template NodeList
        """

        self.nodelist = nodelist

    def render(self, context: template.Context):
        """Render the node list with the given context.
            
        Args:
            context:
        """

        return self.nodelist.render(context)


@register.tag
def djangovue(
    parser: template.base.Parser, token: template.base.Token
) -> DjangoVueNode:
    """Custom django vue tag which can be used to disable django from processing
    template variables. These variables can then be processed by Vue.js on the front-end.

    Args:
        parser:
        token:

    Returns:
        A django vue instance.
    """

    try:
        tag_name, variable_switch = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"'{token.split_contents()[0]}' tag requires a single argument 'on' or 'off'"
        )

    nodelist = template.NodeList()
    for node in parser.parse(("enddjangovue",)):
        if isinstance(node, template.base.VariableNode) and variable_switch == "on":
            nodelist.append(
                template.base.TextNode(f"{{{{ {node.filter_expression} }}}}")
            )
        else:
            nodelist.append(node)

    parser.delete_first_token()

    return DjangoVueNode(nodelist=nodelist)
