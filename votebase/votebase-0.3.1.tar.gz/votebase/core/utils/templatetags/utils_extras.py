from django import template
from django.template import Node, TemplateSyntaxError

register = template.Library()


@register.filter('niceseconds')
def niceseconds(seconds):
    try:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%dh:%02dm:%02ds" % (h, m, s)
    except TypeError:
        return ''


@register.inclusion_tag('backend/helpers/paginator.html', takes_context=True)
def paginator(context, objects, page_ident='page', anchor=None, adjacent_pages=2):
    page_numbers = [n for n in\
                    range(objects.number - adjacent_pages, objects.number + adjacent_pages + 1)\
                    if n > 0 and n <= len(objects.paginator.page_range)]    
    return {
        'anchor': anchor,
        'request': context.get('request', None),
        'page_ident': page_ident,
        'results_per_page': objects.paginator.per_page,
        'page': objects.number,
        'pages': objects.paginator.page_range,
        'count': len(objects.paginator.page_range),
        'page_numbers': page_numbers,
        'next': objects.next_page_number,
        'previous': objects.previous_page_number,
        'has_next': objects.has_next,
        'has_previous': objects.has_previous,
        'show_first': 1 not in page_numbers,
        'show_last': False if len(objects.paginator.page_range) - objects.number <= adjacent_pages else True
    }


@register.filter()
def contains(value, arg):
    url = '/' + '/'.join(value.split('/')[2:])
    if arg == '/':
      return False

    return url in arg


@register.filter()
def get_visited_status(object, user):
    return object.get_visited_status(user)


@register.filter()
def did_user_visit(object, user):    
    return object.did_user_vote(user)


@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.
    
    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    
    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value
    
    # Make sure it's unicode
    value = unicode(value)
    
    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value
    
    # Cut the string
    value = value[:limit]
    
    # Break into words and remove the last
    words = value.split(' ')[:-1]
    
    # Join the words and return
    return ' '.join(words) + '...'


@register.filter
def truncatewords_by_chars(value, arg):
    """Truncate the text when it exceeds a certain number of characters.
    Delete the last word only if partial.
    Adds '...' at the end of the text.

    Example:

        {{ text|truncatewords_by_chars:25 }}
    """
    try:
        length = int(arg)
    except ValueError:
        return value

    if len(value) > length:
        if value[length:length + 1].isspace():
            return value[:length].rstrip() + '...'
        else:
            return value[:length].rsplit(' ', 1)[0].rstrip() + '...'
    else:
        return value


class RangeNode(Node):
    def __init__(self, parser, range_args, context_name):
        self.template_parser = parser
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):

        resolved_ranges = []
        for arg in self.range_args:
            compiled_arg = self.template_parser.compile_filter(arg)
            resolved_ranges.append(compiled_arg.resolve(context, ignore_failures=True))
        context[self.context_name] = range(*resolved_ranges)
        return ""


@register.tag
def mkrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise TemplateSyntaxError, "%s accepts the syntax: {%% %s [start,] " +\
                "stop[, step] as context_name %%}, where 'start', 'stop' " +\
                "and 'step' must all be integers." %(fnctl, fnctl)

    range_args = []
    while True:
        if len(tokens) < 2:
            error()

        token = tokens.pop(0)

        if token == "as":
            break

        range_args.append(token)

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()

    return RangeNode(parser, range_args, context_name)


def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)
raw = register.tag(raw)


@register.filter(is_safe=False)
def divide(value, arg):
    """Divides the value by argument."""
    try:
        return float(value) / float(arg)
    except ZeroDivisionError:
        return float(value)
    except (ValueError, TypeError):
        return ''


@register.filter(is_safe=False)
def multiply(value, arg):
    """Multiplies the value by argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter(is_safe=False)
def add(value, arg):
    """Adds the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter(is_safe=False)
def subtract(value, arg):
    """Subtracts the arg to the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)