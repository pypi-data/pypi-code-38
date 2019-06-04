import time

from django import template
from django.template import NodeList, Node, TemplateSyntaxError
from interruptingcow import timeout, StateException

register = template.Library()


@register.tag()
def timelimit(parser, token):
    """Used to guard section with a timeout:

    {% timelimit 0.05 %}
      <p>No timeout occurred</p>
      {% sleep 0.5 %}
    {% else %}
      <p>timeout!</p>
    {% endtimelimit %}

    @param parser:
    @param token:
    @return:
    """
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise TemplateSyntaxError("No timeout specified")
    end_tag = 'end' + bits[0]

    nodelist_timeout = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_else = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_else = NodeList()

    return TimeoutNode(parser.compile_filter(bits[1]), nodelist_timeout,
                       nodelist_else)


class TimeoutNode(Node):
    def __init__(self, interval, nodelist_timeout, nodelist_else):
        self.interval = interval
        self.nodelist_timeout = nodelist_timeout
        self.nodelist_else = nodelist_else

    def __repr__(self):
        return "<TimeoutNode>"

    def render(self, context):

        class Interrupted(Exception):
            # This class is declared during the render phase to ensure that
            # nested timeout calls don't share the same exception class and
            # then end up catching each other's exceptions.
            pass

        try:
            with timeout(self.interval.resolve(context), Interrupted):
                return self.nodelist_timeout.render(context)
        except StateException:
            # StateException is raised by interruptingcow if its not running
            # on the MainThread. Since not all webservers process requests
            # on the main thread (e.g. Django's own `runserver` command), we
            # swallow the exception and just continue without interruptingcow.
            return self.nodelist_timeout.render(context)
        except Interrupted:
            return self.nodelist_else.render(context)


@register.simple_tag
def sleep(interval):
    # Useful for debugging {% timelimit %}
    time.sleep(float(interval))
    return u''
